import functions_framework
import os
from bs4 import BeautifulSoup
import hashlib
import logging
from datetime import datetime
from google.cloud import pubsub_v1
from google.cloud import logging as glogs
from flask import request
import asyncio

from utils.regex import CardRegex
from utils.url import AsyncHTTPClient


if os.getenv('ENV') == 'prod':
    logging_client = glogs.Client()
    logging_client.setup_logging()
logging.basicConfig(level=logging.INFO)


class MainHTMLPage:
    def __init__(self, html_text, *args, **kwargs):
        self.logger = logging.getLogger('MainHTMLPage')
        self.soup = BeautifulSoup(html_text, "html.parser")
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

    def __init__(self, card, *args, **kwargs):
        self.logger = logging.getLogger('HTMLCard')
        self.logger.debug(f"Processing: {card.text}")
        self.card = card
        self.meta = self._parse_card()
        if kwargs.get('prod'):
            self._push_to_pubsub()

    def _parse_card(self):
        self.logger.debug(f"Regex Matching {self.card.text}")
        meta = CardRegex().match(self.card.text)
        if meta:
            meta['href'] = self.card.get('href')
            meta['_id'] = int(hashlib.sha1(meta['href'].encode(
                "utf-8")).hexdigest(), 16) % (10 ** 8)
        else:
            logging.warning(f"Skipping {self.card.text} no metadata found")
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


def vlidate_args(request):
    if request.args:
        start = int(request.args.get('start', 1))
        end = int(request.args.get('end', start)) + 1
    else:
        start, end = 1, 2
    return start, end


async def _main(request):
    # Validate args
    start, end = vlidate_args(request)
    url, env = os.getenv('BASE_URL'), os.getenv('ENV')
    result = {}
    result['movies'] = []
    prod = True if env == 'prod' else False
    # Generate urls
    urls = [url + f"page/{i}/" for i in range(start, end)]
    # Fetch data Async
    client = AsyncHTTPClient(urls)
    text_data = await client.fetch_all_data()
    await client.close()
    # Parse data
    logging.info(f"Processing {len(text_data)} pages")
    for text in text_data:
        page = MainHTMLPage(text, prod=prod).json()
        for movie in page:
            result['movies'].append(movie)
    result['total'] = len(result['movies'])
    return result


@ functions_framework.http
def main(request):
    result = asyncio.run(_main(request))
    return result


if __name__ == "__main__":
    request = type('', (), {})()
    request.args = {'start': 3, 'end': 3}
    print(main(request))
