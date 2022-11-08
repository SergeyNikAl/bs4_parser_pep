import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import (
    FILE_SAVE_MESSAGE,
    BASE_DIR,
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


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if not response:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections = div_with_ul.find_all('li', attrs={'class': 'toctree-l1'})
    results = [HEADERS_FOR_PYTHON_DOCS_TABLE, ]
    for section in tqdm(sections):
        version_link = urljoin(whats_new_url, section.find('a')['href'])
        response = get_response(session, version_link)
        if not response:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        link_h1 = find_tag(soup, 'h1')
        link_dl = find_tag(soup, 'dl')
        results.append(
            (version_link, link_h1.text, link_dl.text.replace('\n', ' ')))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if not response:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'menu-wrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не найдено')
    results = [HEADERS_FOR_PYTHON_VERSION_TABLE, ]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if not response:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    tables = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(tables, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(FILE_SAVE_MESSAGE.format(path=archive_path))


def pep(session):
    response = get_response(session, MAIN_PEP_URL)
    if not response:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    peps_numerical_section = find_tag(
        soup, 'section', attrs={'id': 'numerical-index'}
    )
    tbody_with_peps_info = find_tag(
        peps_numerical_section, 'tbody'
    )
    tr_peps = tbody_with_peps_info.find_all('tr')
    results = [HEADERS_PEP_TABLE]
    statuses_count = {}
    total = 0
    for pep in tqdm(tr_peps):
        td_pep = find_tag(pep, 'td')
        pep_link = urljoin(MAIN_PEP_URL, pep.find('a')['href'])

        status = td_pep.text[1:]
        response = get_response(session, pep_link)
        if not response:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        status_tag = find_tag(soup, 'dl')
        status_page = status_tag.find(
            string='Status'
        ).parent.find_next_sibling().text
        if status_page not in EXPECTED_STATUS[status]:
            logging.info(
                UNEXPECTED_PEP_STATUS_MESSAGE.format(
                    pep_link=pep_link,
                    status=status_page,
                    expected_status=EXPECTED_STATUS[status],
                )
            )
        statuses_count[status_page] = statuses_count.get(status_page, 0) + 1
        total += 1
        results[1:] = [
            (status, amount) for status, amount in statuses_count.items()
        ]
        results += [('Total', total)]
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')
    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    # Получение из аргументов командной строки нужного режима работы.
    parser_mode = args.mode
    # Поиск и вызов нужной функции по ключу словаря.
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
