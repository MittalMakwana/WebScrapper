import functions_framework
import os
import requests
import re
from bs4 import BeautifulSoup
import hashlib
import logging
from datetime import datetime
from google.cloud import pubsub_v1
from google.cloud import logging as glogs
from flask import request

if os.getenv('ENV') == 'prod':
    logging_client = glogs.Client()
    logging_client.setup_logging()
logging.basicConfig(level=logging.INFO)


class CardRegex:
    _name = r'(?P<name>.*)'
    _size = r'(?P<size>.*)'
    _quality = r'(?P<quality>\d+p)'
    _type = r'(?P<type>\w*)'
    _day = r'(?P<day>\d+)'
    _month = r'(?P<month>.+)\s?'
    _yr = r'(?P<yr>\d\d\d\d)?'
    _ordinal = r'(st|nd|rd|th)?\s'
    _ep = r'(?P<ep>(?:S\d*(EP?\d*T?O?\d*)?)?)'
    _part = r'(Part \d)?\s?'
    _view_type = r'(?P<view_type>3D|V2)\s'
    _str = rf"{_name}\s(\((?P<dt>(?:{_day}{_ordinal}{_month})?{_yr})\)\s+)\s?{_ep}\s?{_part}({_view_type})?{_quality}\s?{_type}(.*)\[{_size}\]$"
    CARD_REGEX = re.compile(_str)

    def __init__(self):
        self.regex = self.CARD_REGEX

    def match(self, card):
        return self.regex.match(card).groupdict()

    def __repr__(self) -> str:
        return self._str


class MainHTMLPage:
    def __init__(self, url, *args, **kwargs):
        self.logger = logging.getLogger('MainHTMLPage')
        self.url = url
        self.logger.info(f"Fetching {self.url}")
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.logger.info("Parsing HTML")
        self.cards = self.soup.find_all('a', {"class": "thumbtitle"})
        self.meta = self._gen_meta(*args, **kwargs)

    def json(self):
        return self.meta

    def __len__(self):
        return len(self.cards)

    def _gen_meta(self, *args, **kwargs):
        meta = []
        for card in self.cards:
            meta.append(HTMLCard(card, *args, **kwargs).meta)
        return meta


class HTMLCard:
    CARD_REGEX = CardRegex()

    def __init__(self, card, *args, **kwargs):
        self.logger = logging.getLogger('HTMLCard')
        self.logger.debug(f"Processing: {card.text}")
        self.card = card
        self.meta = self._parse_card()
        if kwargs.get('prod'):
            self._push_to_pubsub()

    def _parse_card(self):
        meta = {}
        self.logger.debug(f"Regex Matching {self.card.text}")
        try:
            meta = self.CARD_REGEX.match(self.card.text)
            meta['href'] = self.card.get('href')
            meta['_id'] = int(hashlib.sha1(meta['href'].encode(
                "utf-8")).hexdigest(), 16) % (10 ** 8)
        except AttributeError:
            self.logger.error(f"Regex not matched for {self.card.text}")
        return meta

    def _push_to_pubsub(self):
        if self.meta.get('_id'):
            self.logger.info(f"Pushing {self.meta['name']} to pubsub")
            project_id = os.getenv('PROJECT_ID')
            topic_id = os.getenv('TOPIC_ID')
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(project_id, topic_id)
            event_time = datetime.utcnow()
            attributes = {
                'id': str(self.meta['_id']),
            }
            publisher.publish(topic_path, str(self.meta).encode(
                "utf-8"), attributes=str(attributes).encode("utf-8"))
        else:
            logging.warning(f"Skipping {self.card.text} no metadata found")


@functions_framework.http
def main(request):
    if request.args:
        start = int(request.args.get('start'))
        end = int(request.args.get('end'))
    else:
        start, end = 1, 2
    prod = False
    URL = os.getenv('BASE_URL')
    env = os.getenv('ENV')
    result = {}
    result['movies'] = []
    if env == 'prod':
        prod = True
    for i in range(start, end):
        _URL = URL + f"page/{i}/"
        page = MainHTMLPage(_URL, prod=prod).json()
        for movie in page:
            result['movies'].append(movie)
    result['total'] = len(result['movies'])
    return result


if __name__ == "__main__":
    # print(repr(CardRegex()))
    request = type('', (), {})()
    request.args = {'start': 1, 'end': 3}
    print(main(request))
