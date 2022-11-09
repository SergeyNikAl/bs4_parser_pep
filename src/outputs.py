import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    BASE_DIR,
    DATETIME_FORMAT,
    FILE_MOD,
    FILE_SAVE_MESSAGE,
    PRETTY_MOD,
    RESULTS_DIR
)


def default_output(results, *args):
    for row in results:
        print(*row)


def pretty_output(results, *args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now_formatted = dt.datetime.now().strftime(DATETIME_FORMAT)
    file_path = results_dir / f'{parser_mode}_{now_formatted}.csv'
    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(FILE_SAVE_MESSAGE.format(path=file_path))


OUTPUT_FUNCTIONS = {
    FILE_MOD: file_output,
    PRETTY_MOD: pretty_output,
    None: default_output,
}


def control_output(results, cli_args, outputs=OUTPUT_FUNCTIONS):
    outputs[cli_args.output](results, cli_args)
