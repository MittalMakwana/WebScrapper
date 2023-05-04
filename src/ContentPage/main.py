import functions_framework
import os
import requests
import re
from bs4 import BeautifulSoup
import logging
import base64
import ast
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)


class ContentPage:
    dl_link_base_url = os.environ.get('DL_LINK_BASE_URL')

    def __init__(self, url):
        self.logger = logging.getLogger('ContentPage')
        logging.info(f'Prcessing: {url}')
        self.url = url
        self.meta = self._gen_meta()

    def _gen_meta(self):
        self.meta = {}
        self.page = requests.get(self.url)
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        self.dl_link = self.soup.find('a', {"class": "hsl"})
        self.poster, self.thumbnils = self.soup.find_all(
            'img', {"decoding": "async"})[:2]
        self.meta['thumbnil'] = self.thumbnils.get('src')
        self.meta['poster'] = self.poster.get('src')
        self.meta['sublink'] = self.dl_link.get('href')
        self.meta['dl_link'] = self._get_dl_link()
        return self.meta

    def _get_dl_link(self):
        # Get the w3down link
        page = requests.get(self.meta['sublink'])
        soup = BeautifulSoup(page.content, "html.parser")
        next_page_url = self.dl_link_base_url + \
            soup.find_all('a')[1].get('href')
        get_next_page = requests.get(next_page_url)
        soup = BeautifulSoup(get_next_page.content, "html.parser")
        urls = list(soup.find_all('input'))
        url_list = [_url.get('value').rstrip() for _url in urls]
        return url_list

    def json(self):
        return self.meta


def parse_message(message):  # <-- This message is base64 string
    data = base64.b64decode(message)
    data = ast.literal_eval(data.decode('utf-8'))
    dl_links = ContentPage(data.get('href')).json()
    data.update(dl_links)
    return data


def write_to_db(meta_data):
    env = os.getenv('ENV')
    if env == 'prod':
        sm_client = secretmanager.SecretManagerServiceClient()
        name = "projects/469329805118/secrets/MONGO_DB_PWD/versions/latest"
        response = sm_client.access_secret_version(name=name)
        secret_value = response.payload.data.decode("UTF-8")
        # Set the secret value as an environment variable
        os.environ["MONGO_DB_PWD"] = secret_value

    client = MongoClient(
        f"mongodb+srv://{os.getenv('MONGO_DB_USER')}:{os.getenv('MONGO_DB_PWD')}@{os.getenv('MONGO_DB_HOST')}")

    db = client["9xmovies"] if env == 'prod' else client["9x_movies_dev"]
    collection = db['dl_link']
    try:
        collection.insert_one(meta_data)
        logging.info(f"Added collection:{meta_data['_id']}")
    except DuplicateKeyError:
        logging.info(f"Document already exsit skipping {meta_data['_id']}")
    pass


@functions_framework.cloud_event
def main(cloud_event, *args, **kwargs):
    env = os.getenv('ENV')
    if env == 'dev':
        meta_data = ContentPage(kwargs['url']).json()
        meta_data['_id'] = 1
        logging.info(meta_data)
    elif env == 'prod':
        meta_data = parse_message(cloud_event.data['message']['data'])

    write_to_db(meta_data)


if __name__ == "__main__":
    kwargs = {'url': 'https://9xmovie.best/challenging-stepmom-mia-khalifa-2023-720p-hdrip-english-adult-video-100mb/'}
    main(None, **kwargs)
