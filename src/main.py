import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR,
    CONNECTION_ERROR_MESSAGE,
    DOWNLOAD_DIR,
    FILE_SAVE_MESSAGE,
    FINISH_PARSING_MESSAGE,
    EXPECTED_STATUS,
    HEADERS_FOR_PYTHON_DOCS_TABLE,
    HEADERS_FOR_PYTHON_VERSION_TABLE,
    HEADERS_PEP_TABLE,
    MAIN_DOC_URL,
    MAIN_PEP_URL,
    NOT_FOUND_TAG_MESSAGE,
    PARSING_WITH_ARGUMENTS_MESSAGE,
    PROGRAM_ERROR_MESSAGE,
    PYTHON_VERSION_ERROR_MESSAGE,
    START_PARSING_MESSAGE,
    UNEXPECTED_PEP_STATUS_MESSAGE,
)
from exceptions import ParserFindTagException
from outputs import control_output
from utils import find_tag, get_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    sections = get_soup(session, whats_new_url).select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    results = [HEADERS_FOR_PYTHON_DOCS_TABLE, ]
    for section in tqdm(sections):
        version_link = urljoin(whats_new_url, section.find('a')['href'])
        try:
            soup = get_soup(session, version_link)
            results.append(
                (
                    version_link,
                    find_tag(soup, 'h1').text,
                    find_tag(soup, 'dl').text.replace('\n', ' ')
                )
            )
        except ConnectionError:
            continue
    return results


def latest_versions(session):
    ul_tags = get_soup(session, MAIN_DOC_URL).select('div.menu-wrapper ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise RuntimeError(PYTHON_VERSION_ERROR_MESSAGE)
    results = [HEADERS_FOR_PYTHON_VERSION_TABLE, ]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag['href'], version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    pdf_a4_tag = get_soup(session, downloads_url).select_one(
        'table.docutils td > a[href$="pdf-a4.zip"]'
    )
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    filename = archive_url.split('/')[-1]
    download_dir = BASE_DIR / DOWNLOAD_DIR
    download_dir.mkdir(exist_ok=True)
    archive_path = download_dir / filename
    with open(archive_path, 'wb') as file:
        file.write(session.get(archive_url).content)
    logging.info(FILE_SAVE_MESSAGE.format(path=archive_path))


def pep(session):
    logs = []
    statuses_count = defaultdict(int)
    for pep in tqdm(get_soup(
        session, MAIN_PEP_URL
    ).select(
        '#numerical-index tbody tr'
    )):
        pep_link = urljoin(MAIN_PEP_URL, pep.find('a')['href'])
        try:
            status = find_tag(pep, 'td').text[1:]
            status_page = find_tag(
                get_soup(session, pep_link), 'dl'
            ).find(
                string='Status'
            ).parent.find_next_sibling().text
            if status_page not in EXPECTED_STATUS[status]:
                logs.append(
                    UNEXPECTED_PEP_STATUS_MESSAGE.format(
                        pep_link=pep_link,
                        status=status_page,
                        expected_status=EXPECTED_STATUS[status],
                    )
                )
            statuses_count[status_page] += 1
        except ConnectionError:
            logs.append(CONNECTION_ERROR_MESSAGE.format(link=pep_link))
        except ParserFindTagException:
            logs.append(NOT_FOUND_TAG_MESSAGE)
    for log in logs:
        logging.info(log)
    return [
        HEADERS_PEP_TABLE,
        *statuses_count.items(),
        ('Total', sum(statuses_count.values()))
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info(START_PARSING_MESSAGE)
    args = configure_argument_parser(MODE_TO_FUNCTION.keys()).parse_args()
    logging.info(PARSING_WITH_ARGUMENTS_MESSAGE.format(args=args))
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results:
            control_output(results, args)
    except Exception as error:
        logging.exception(
            msg=PROGRAM_ERROR_MESSAGE.format(error=error),
            stack_info=True
        )
    logging.info(FINISH_PARSING_MESSAGE)


if __name__ == '__main__':
    main()
