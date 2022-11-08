# Проект парсинга pep

## Оглавление
- [Оглавление](#оглавление)
- [Используемые технологии](#используемые-технологии)
- [Структура проекта](#структура-проекта)
- [Документация парсера](#документация-парсера)
- [Описание проекта](#описание-проекта)
- [Запуск проекта](#запуск-проекта)

## Используемые технологии
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) 4.9.3
- [lxml](https://pypi.org/project/lxml/) 4.9.1
- [PrettyTable](https://pypi.org/project/prettytable/) 2.1.0
- [requests-cache](https://pypi.org/project/requests-cache/) 0.6.3
- [tqdm](https://pypi.org/project/tqdm/) 4.61.0

## Структура проекта
```
bs4_parser_pep
 ├── src/
     ├── __init__.py
     ├── configs.py
     ├── constants.py
     ├── exceptions.py
     ├── main.py
     ├── outputs.py
     └── utils.py
 ├── tests/
 ├── .flake8
 ├── .gitignore
 ├── README.md
 ├── pytest.ini
 └── requirements.txt
```

## Документация парсера
```
usage: main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}

Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

options:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных

```

## Описание проекта
Парсер собирает иформацию сайта документации Python ```https://docs.python.org/3/``` и каталога с PEP ```https://peps.python.org/```.

Режимы работы:
- ```whats-new``` - Парсер статей по нововведениям в Python;
- ```latest-versions``` - Статусы последних версий со ссылками на документацию;
- ```download``` - Скачивание документации по последней версии Python;
- ```pep``` - Формирование таблицы с количеством PEP в разрезе по статусам;

Моды по выводу итогов парсинга:
- ```-o pretty``` - вывод результатов в консоль в виде таблицы;
- ```-o file``` - вывод результатов в виде **.csv** файла, который сохраняется в директорию ***/results***;
- без указания команды по выводу результатов, итоги выводтся в консоль в строчку.

Дополнительные опциональные аргументы можно узнать из [Документации парсера](#документация-парсера) или вызвать файл ```main.py``` c аргументом ```-h```.

[:top: Вернуться к оглавлению](#оглавление)

---
<details><summary>Подробнее о режимах работы парсера:</summary>
<p>

Режим работы ```whats-new``` сканирует страницу ```https://docs.python.org/3/```, раздел ***"Docs by version"***, и собирает ссылки на каждую версию ***Python***. Далее сканирует карточку каждой версии ***Python*** и выводит информацию: ссылка на статью, заголовок, редактор, автор.

```
Пример:
$ python main.py -o pretty whats-new

+----------------------------------------------+---------------------------+-----------------------------------------------------------------------+
| Ссылка на статью                             | Заголовок                 | Редактор, Автор                                                       |
+----------------------------------------------+---------------------------+-----------------------------------------------------------------------+
| https://docs.python.org/3/whatsnew/3.11.html | What’s New In Python 3.11 |  Release 3.11.0  Date November 08, 2022  Editor Pablo Galindo Salgado |
| ...                                          | ...                       |  ...                                                                  |
+----------------------------------------------+---------------------------+-----------------------------------------------------------------------+
```
---

Режим работы ```latest-versions``` сканирует страницу ```https://docs.python.org/3/```, раздел ***"Docs by version"*** и выводит информацию о **Python**: ссылку на документацию, версия и статус.

```
Пример:
python main.py -o pretty latest-versions

+--------------------------------------+--------------+----------------+
| Ссылка на документацию               | Версия       | Статус         |
+--------------------------------------+--------------+----------------+
| https://docs.python.org/3.12/        | 3.12         | in development |
| https://docs.python.org/3.11/        | 3.11         | stable         |
| https://docs.python.org/3.10/        | 3.10         | stable         |
| https://docs.python.org/3.9/         | 3.9          | security-fixes |
| https://docs.python.org/3.8/         | 3.8          | security-fixes |
| https://docs.python.org/3.7/         | 3.7          | security-fixes |
| https://docs.python.org/3.6/         | 3.6          | EOL            |
| https://docs.python.org/3.5/         | 3.5          | EOL            |
| https://docs.python.org/2.7/         | 2.7          | EOL            |
| https://www.python.org/doc/versions/ | All versions |                |
+--------------------------------------+--------------+----------------+

```
---
Режим работы ```download``` сканирует страницу ```https://docs.python.org/3/download.html``` и скачивает PDF-файл документации zip-архивом. Архив сохраняется в директорию ***/downloads***.

---
Режим работы ```pep``` сканирует страницу ```https://peps.python.org/```, собирает статусы всех **PEP**, ссылки на каждый **PEP** и подсчитывает общее количество **PEP**.
Так как статусы на общей странице **PEP** различаются со статусом в карточке каждого **PEP**, парсер дополнительно проходит по карточке каждого **PEP** и собирает его статус, параллельно сравнивая со статусом из общей таблицы с **PEP**. Если статусы различиются, то информация записывается в логи, уровень **INFO**.

```
Пример:

Несовпадающие статусы:
https://peps.python.org/pep-0401
Статус в карточке pep: April Fool!
Ожидаемые статусы: ('Rejected',)
```

[:top: Вернуться к оглавлению](#оглавление)

---
</p>
</details>


## Запуск проекта
1. Клонировать репозиторий:
```bash
git clone https://github.com/SergeyNikAl/bs4_parser_pep
```

2. Создать виртуальное окружение:
```bash
python3 -m venv venv
```

3. Активировать виртуальное окружение и установить зависимости из ```requirements.txt```:
```bash
source venv/Scripts/activate
```

```bash
pip install -r requirements.txt
```

4. Запустить ```main.py``` и ознакомиться с [документацией парсера](#документация-парсера):
```bash
python3 main.py -h
```
[:top: Вернуться к оглавлению](#оглавление)