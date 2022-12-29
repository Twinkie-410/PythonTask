import pandas as pd
import sqlite3

def get_sql_table():
    """
    Переводит введный csv-файл в таблицу sqlite.
    """
    df = pd.read_csv(input('Введите нужный csv-файл: '))
    conn = sqlite3.connect('valCurs.sqlite')
    df.to_sql('valCurs', conn, if_exists='replace', index=False)

get_sql_table()