import csv


def get_vacancies_by_year(file_path="..\\..\\Data\\vacancies_by_year.csv"):
    """
    Функция по разбиению вакансий по годам
    :param file_path: str
    :return: (dict[str, str[]], str[])
        словарь: ключи - года вакансий
                 значения - вакансии соответсвующего года публикации
        массив заголовков
    """
    with open(file_path, "r", encoding='utf_8_sig') as file:
        reader = csv.reader(file)
        headers = next(reader, None)
        dict_vac_by_year = {}
        for line in reader:
            year = line[5][:4]
            if year not in dict_vac_by_year.keys():
                dict_vac_by_year[year] = [line]
            else:
                dict_vac_by_year[year].append(line)

    return dict_vac_by_year, headers


def write_to_csv(data_by_year, headers):
    """
    Формирует файлы с вакансиями по годам
    :param data_by_year: dict[str, str[]]
        словарь с вакансиями по годам
    :param headers: str[]
    """
    for key, value in data_by_year.items():
        with open(f"..\\data_by_year\\part_{key}.csv", "w", encoding="utf-8") as file:
            by_write = [headers, *value]
            writer = csv.writer(file, delimiter=",")
            writer.writerows(by_write)


vac_by_year, title = get_vacancies_by_year()
write_to_csv(vac_by_year, title)
