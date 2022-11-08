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
        logging.exception(
            PAGE_LOADING_ERROR_MESSAGE.format(url=url),
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if not searched_tag:
        error_msg = MISSING_TAG_MESSAGE.format(tag=tag, attrs=attrs)
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
