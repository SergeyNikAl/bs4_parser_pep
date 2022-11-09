from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'

PRETTY_MOD = 'pretty'
FILE_MOD = 'file'

BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = 'downloads'
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
RESULTS_DIR = 'results'

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'



CONNECTION_ERROR_MESSAGE = 'Не удалось установить соединение по ссылке {link}'
FILE_SAVE_MESSAGE = 'Файл был загружен и сохранён: {path}'
FINISH_PARSING_MESSAGE = 'Парсер завершил работу.'
HEADERS_FOR_PYTHON_DOCS_TABLE = (
    'Ссылка на статью', 'Заголовок', 'Редактор, Автор'
)
HEADERS_FOR_PYTHON_VERSION_TABLE = (
    'Ссылка на документацию', 'Версия', 'Статус'
)
HEADERS_PEP_TABLE = ('Статус', 'Количество')
PAGE_LOADING_ERROR_MESSAGE = 'Возникла ошибка при загрузке страницы {url}'
PARSING_WITH_ARGUMENTS_MESSAGE = 'Аргументы командной строки: {args}'
START_PARSING_MESSAGE = 'Парсер запущен!'
MISSING_TAG_MESSAGE = 'Не найден тег {tag} {attrs}'
NOT_FOUND_TAG_MESSAGE = 'Тэг не найден'
PROGRAM_ERROR_MESSAGE = 'Сбой в работе программы: {error}'
PYTHON_VERSION_ERROR_MESSAGE = 'Версий Python не найдено'
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
    '': ('Draft', 'Active',),
}
