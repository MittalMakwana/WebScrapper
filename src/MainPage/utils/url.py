import aiohttp
import asyncio
import logging

logging.basicConfig(level=logging.INFO)


class AsyncHTTPClient:
    def __init__(self, urls):
        self.urls = urls
        self.session = aiohttp.ClientSession()

    async def fetch_data(self, url):
        try:
            logging.info(f"Featching data from {url}")
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.text()
                    return data
                else:
                    return None
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None

    async def fetch_all_data(self):
        tasks = []
        for url in self.urls:
            task = asyncio.create_task(self.fetch_data(url))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def close(self):
        await self.session.close()
