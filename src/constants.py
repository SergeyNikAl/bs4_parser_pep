from pathlib import Path

BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
PAGE_LOADING_ERROR_MESSAGE = 'Возникла ошибка при загрузке страницы {url}'
MISSING_TAG_MESSAGE = 'Не найден тег {tag} {attrs}'
HEADERS_FOR_PYTHON_DOCS_TABLE = (
    'Ссылка на статью', 'Заголовок', 'Редактор, Автор'
)
HEADERS_FOR_PYTHON_VERSION_TABLE = (
    'Ссылка на документацию', 'Версия', 'Статус'
)
HEADERS_PEP_TABLE = ('Статус', 'Количество')
FILE_SAVE_MESSAGE = 'Файл был загружен и сохранён: {path}'
UNEXPECTED_PEP_STATUS_MESSAGE = (
    '{pep_link}\nСтатус в карточке pep: {status}\n'
    'Ожидаемые статусы: {expected_status}'
)
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
