import logging
from requests import RequestException

from constants import PAGE_LOADING_ERROR_MESSAGE, MISSING_TAG_MESSAGE
from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        raise ConnectionError(logging.exception(
            PAGE_LOADING_ERROR_MESSAGE.format(url=url),
            stack_info=True
        ))


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=({} if attrs is None else attrs))
    if not searched_tag:
        raise ParserFindTagException(
            MISSING_TAG_MESSAGE.format(tag=tag, attrs=attrs)
        )
    return searched_tag
