import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import (
    BASE_DIR,
    DOWNLOAD_DIR,
    EXECUTION_ERROR,
    FILE_SAVE_MESSAGE,
    EXPECTED_STATUS,
    HEADERS_FOR_PYTHON_DOCS_TABLE,
    HEADERS_FOR_PYTHON_VERSION_TABLE,
    HEADERS_PEP_TABLE,
    MAIN_DOC_URL,
    MAIN_PEP_URL,
    UNEXPECTED_PEP_STATUS_MESSAGE,
)
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import find_tag, get_response


def get_soup(session, *args):
    response = get_response(session, *args)
    if not response:
        return
    return BeautifulSoup(response.text, features='lxml')


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    sections = get_soup(session, whats_new_url).select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    results = [HEADERS_FOR_PYTHON_DOCS_TABLE, ]
    for section in tqdm(sections):
        version_link = urljoin(whats_new_url, section.find('a')['href'])
        soup = get_soup(session, version_link)
        results.append(
            (
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
            )
        )
    return results


def latest_versions(session):
    ul_tags = get_soup(session, MAIN_DOC_URL).select('div.menu-wrapper ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise RuntimeError('Ничего не найдено')
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
    tr_peps = get_soup(
        session, MAIN_PEP_URL
    ).select(
        '#numerical-index tbody tr'
    )
    logs = []
    statuses_count = defaultdict(int)
    for pep in tqdm(tr_peps):
        td_pep = find_tag(pep, 'td')
        pep_link = urljoin(MAIN_PEP_URL, pep.find('a')['href'])
        status = td_pep.text[1:]
        soup = get_soup(session, pep_link)
        status_tag = find_tag(soup, 'dl')
        status_page = status_tag.find(
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
    for log in logs:
        logging.info(log)
    return [
        HEADERS_PEP_TABLE,
        *[(status, amount) for status, amount in statuses_count.items()],
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
    logging.info('Парсер запущен!')
    args = configure_argument_parser(MODE_TO_FUNCTION.keys()).parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results:
            control_output(results, args)
    except Exception:
        logging.exception(msg=EXECUTION_ERROR, stack_info=True)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
