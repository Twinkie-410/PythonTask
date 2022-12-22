import csv
import pandas as pd

def calculate(s_from, s_to, currency, date, rub_exchange_rate):
    salary = float(s_from) if s_from != "" else 0
    salary += float(s_to) if s_to != "" else 0
    ratio = 1
    if currency != "RUR" and currency in rub_exchange_rate.columns:
        ratio = rub_exchange_rate[rub_exchange_rate["Date"] == date[:7]][currency].values[0]
    return "" if salary == 0 or currency not in rub_exchange_rate.columns else float(round(salary * ratio))

def join_salaries_field(needed_count_vacancies, file_path = "..\\..\\Data\\vacancies_dif_currencies.csv"):
    rub_exchange_rate = pd.read_csv("currencies.csv")
    with open(file_path, "r", encoding="utf_8_sig") as file:
        with open("processed_vacancies.csv", "w", encoding="utf_8", newline='') as file_write:
            reader_csv = csv.reader(file)
            writer = csv.writer(file_write)
            writer.writerow(["name", "salary", "area_name", "published_at"])
            reader_csv.__next__()
            for i, x in enumerate(reader_csv):
                salary = calculate(x[1], x[2], x[3], x[5], rub_exchange_rate)
                writer.writerow([x[0], salary, x[4], x[5]])
                if i == needed_count_vacancies - 1:
                    break

join_salaries_field(100)