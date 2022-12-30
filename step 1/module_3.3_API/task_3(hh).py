import csv
import time
import requests

def get_page(page, time_from, time_to, date):
    """
    Получает ответ на запрос с api.hh.ru: список IT-вакансий в формате .json.
    :param page: Номер страницы, с которой приходит вакансия (int)
    :param time_from: Начало временного промежутка, с которого начинается выбор вакансии (str)
    :param time_to: Конец временного промежутка, на котором заканчивается выбор вакансии (str)
    :param date: Дата, когда была опубликована вакансия (str)
    :return: Список IT-вакансий в формате .json
    """
    params = {
        'specialization': 1,
        'page': page,
        'per_page': 100,
        'date_from': f'{date}T{time_from}+0300',
        'date_to': f'{date}T{time_to}+0300',
    }

    req = requests.get('https://api.hh.ru/vacancies', params).json()
    return req

def add_csv_vacancy():
    """
    Добавляет нужные поля вакансии в CSV-файл, итерируясь по страницам и промежуткам времени.
    """
    for hour in range(0, 23, 2):
        next_hour = hour + 1
        if hour < 10:
            hour = f'0{hour}'
        if next_hour < 10:
            next_hour = f'0{next_hour}'
        for page in range(0, 20):
            vacancies = get_page(page, f'{hour}:00:00', f'{next_hour}:59:59', '2022-12-20')
            with open(f"hhVacancies.csv", mode="a", encoding='utf-8-sig') as w_file:
                file_writer = csv.writer(w_file, delimiter=',', lineterminator="\r")
                for row in vacancies['items']:
                    if row['salary'] is None:
                        file_writer.writerow([row['name'], '', '', '', row['area']['name'], row['published_at']])
                    else:
                        file_writer.writerow([row['name'], row['salary']['from'], row['salary']['to'],
                                              row['salary']['currency'], row['area']['name'], row['published_at']])

            if (vacancies['pages'] - page) <= 1:
                break

            time.sleep(0.25)

if __name__ == '__main__':
    with open(f"hhVacancies.csv", mode="a", encoding='utf-8-sig') as w_file:
        file_writer = csv.writer(w_file, delimiter=',', lineterminator="\r")
        file_writer.writerow(['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at'])
    add_csv_vacancy()


