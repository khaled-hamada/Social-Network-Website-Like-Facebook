""" Asynchronously get links embedded in multiple pages' HTML  """

import asyncio
import logging
import re
import sys
from typing import IO
import urllib.error
import urllib.parse
from random import randint

import aiohttp
from aiohttp import ClientSession
from images.forms import ImageCreateForm
from images.models import Image
from django.contrib.auth import get_user_model

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)

logger = logging.getLogger("asyncReq")
logging.getLogger("chardet.charsetprober").disabled = True

IMAGE_URL = re.compile(r'src="(.*?)"')
USER = get_user_model().objects.get(username="admin")

async def fetch_html(url: str, session: ClientSession, **kwargs) -> str:
    """GET request wrapper to fetch page HTML.

    kwargs are passed to `session.request()`.
    """
    # let exceptions handled by the calller
    resp = await session.request(method='GET', url=url, **kwargs)
    resp.raise_for_status()  # raise if status >= 400 errors
    logger.info("Got response[%s] for URL: %s", resp.status, url)
    html = await resp.text()  # for # bytes use => resp.read()
    #do not close session let the caller decide when to close it
    return html


async def parse(url: str, session: ClientSession, **kwargs) -> set:
    """ Find unique set of HREFs in the HTML of `url` """
    found = set()
    try:
        html = await fetch_html(url, session, **kwargs)
    except (
        aiohttp.ClientError,
        aiohttp.http_exceptions.HttpProcessingError,
    ) as e:
        logger.error(
            "aiohttp exception for %s [%s: %s]",
            url,
            getattr(e, "status", None),
            getattr(e, "message", None)
        )
        return found  # empty set

    except Exception as e:
        # May be raised from other libraries, such as chardet or yarl.
        # logger.exception will show the full traceback.
        logger.exception(
            "Non-aiohttp exception occured:%s ",
            getattr(e, "__dict__", {})
        )
        return found
    else:  # no exceptions
        # This portion is not really async, but it is the request/response
        # IO cycle that eats the largest portion of time
        for link in IMAGE_URL.findall(html):
            print('link, ', link)
            image_title = "image-" + "".join([chr(randint(97, 122)) for i in range(15)]);
            try:
                data = {
                    'title':image_title,
                    "url":link,
                    "description":image_title,
                }
                form = ImageCreateForm(data = data)
                #form is submitted from user
                if form.is_valid():
                    # create a new instance but do not save to associate user to it
                    new_item = form.save(commit=False)
                    new_item.user = USER
                    new_item.save()
                   
            except (urllib.error.URLError, ValueError):
                logger.exception("Error parsing URL: %s", link)

        logger.info("found %d links for %s", len(found), url)
        return found




async def bulk_crawl_and_write(urls: set, **kwargs) -> None:
    async with ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(
                asyncio.create_task(
                    parse(url=url, session=session, **kwargs))
            )
        await asyncio.gather(*tasks)

def crawler():
    import pathlib
    import sys

    assert sys.version_info >= (3, 7), "Script requires python 3.7+"
    here = pathlib.Path(__file__).parent

    with open(here.joinpath('urls.txt')) as infile:
        # lst = [str.strip(line) for line in infile]
        # urls = set(lst)
        urls = set(map(str.strip, infile))
    # urls = set(["https://www.amazon.com/",
    #             "https://www.alibaba.com/",
    #             "https://pixabay.com/",
    #             ])
    # event_loop = asyncio.get_event_loop()
    # event_loop.run_until_complete(
    #     bulk_crawl_and_write(file=outpath, urls=urls))
    asyncio.run(bulk_crawl_and_write(urls=urls))

if __name__ == '__main__':
    import pathlib
    import sys

    assert sys.version_info >= (3, 7), "Script requires python 3.7+"
    here = pathlib.Path(__file__).parent

    with open(here.joinpath('urls.txt')) as infile:
        # lst = [str.strip(line) for line in infile]
        # urls = set(lst)
        urls = set(map(str.strip, infile))

    # event_loop = asyncio.get_event_loop()
    # event_loop.run_until_complete(
    #     bulk_crawl_and_write(file=outpath, urls=urls))
    asyncio.run(bulk_crawl_and_write(urls=urls))
