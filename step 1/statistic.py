import csv
import datetime
import re
import matplotlib.pyplot as plt
import pdfkit
from matplotlib.ticker import IndexLocator
from jinja2 import Environment, FileSystemLoader


class DictByCity:
    """
    Словарь для формирования статистики по городам
    Atributes
    ---------
    data_dict : dict[str, [int, int]]
        данные словаря: [город, [суммарный оклад, кол-во вакансий]]
    total_count : int
        всего вакансий
    """

    def __init__(self):
        """
        Инициализация обьекта
        """
        self.data_dict = {}
        self.total_count = 0

    def add_data(self, city, value):
        """
        Добавляет элемент в словарь
        :param city: str
            город
        :param value: int
            средний оклад
        """
        if city not in self.data_dict.keys():
            self.data_dict[city] = [value, 1]
        else:
            self.data_dict[city][0] += value
            self.data_dict[city][1] += 1
        self.total_count += 1

    def get_by_salary(self):
        """
        :return: dict[str, int]
            ранжированные данные по среднему окладу в виде: город - средний оклад


        >>> t = DictByCity()
        >>> t.data_dict, t.total_count = {"№1": [120000, 3], "№2": [60000, 1], "№3": [90000, 4], "№4": [280000, 20]}, 28
        >>> t.get_by_salary()
        {'№2': 60000, '№1': 40000, '№3': 22500, '№4': 14000}

        >>> t = DictByCity()
        >>> t.data_dict, t.total_count = {"№1": [120000, 3], "№2": [60000, 1], "№3": [90000, 4], "№4": [280000, 20]}, 103
        >>> t.get_by_salary()
        {'№1': 40000, '№3': 22500, '№4': 14000}

        >>> t = DictByCity()
        >>> t.data_dict = {"№1": [120000, 3], "№2": [60000, 1], "№3": [900000, 15], "№4": [280000, 20], "№5": [1000000, 10], "№6": [5000000, 30], "№7": [2800000, 14], "№8": [1000000, 10], "№9": [420000, 7], "№10": [580000, 9], "№11": [400000, 4], "№12": [280000, 4], "№13": [531000, 15]}
        >>> t.total_count = 142
        >>> t.get_by_salary()
        {'№7': 200000, '№6': 166666, '№5': 100000, '№8': 100000, '№11': 100000, '№12': 70000, '№10': 64444, '№3': 60000, '№9': 60000, '№1': 40000}

        >>> t = DictByCity()
        >>> t.get_by_salary()
        {}

        """
        sub_dict = {}
        sort_dic = dict(sorted(self.data_dict.items(), key=lambda item: item[1][0] // item[1][1], reverse=True))
        for key, value in sort_dic.items():
            ratio = value[1] / self.total_count
            if ratio >= 0.01:
                sub_dict[key] = int(value[0] // value[1])
            if len(sub_dict) == 10:
                break

        return sub_dict

    def get_by_count(self):
        """
        :return: dict[str, float]
            данные в виде: город - доля вакансий от общего количества

        >>> t = DictByCity()
        >>> t.data_dict, t.total_count = {"№1": [120000, 3], "№2": [60000, 1], "№3": [90000, 4], "№4": [280000, 20]}, 28
        >>> t.get_by_count()
        {'№4': 0.7143, '№3': 0.1429, '№1': 0.1071, '№2': 0.0357}

        >>> t = DictByCity()
        >>> t.data_dict, t.total_count = {"№1": [120000, 3], "№2": [60000, 1], "№3": [90000, 4], "№4": [280000, 20]}, 103
        >>> t.get_by_count()
        {'№4': 0.1942, '№3': 0.0388, '№1': 0.0291}

        >>> t = DictByCity()
        >>> t.data_dict = {"№1": [120000, 3], "№2": [60000, 1], "№3": [900000, 15], "№4": [280000, 20], "№5": [1000000, 10], "№6": [5000000, 30], "№7": [2800000, 14], "№8": [1000000, 10], "№9": [420000, 7], "№10": [580000, 9], "№11": [400000, 4], "№12": [280000, 4], "№13": [531000, 15]}
        >>> t.total_count = 142
        >>> t.get_by_count()
        {'№6': 0.2113, '№4': 0.1408, '№3': 0.1056, '№13': 0.1056, '№7': 0.0986, '№5': 0.0704, '№8': 0.0704, '№10': 0.0634, '№9': 0.0493, '№11': 0.0282, 'Другие': 0.0563}

        >>> t = DictByCity()
        >>> t.get_by_count()
        {}
        """
        sub_dict = {}
        sort_dic = dict(sorted(self.data_dict.items(), key=lambda item: item[1][1], reverse=True))
        count_top_city = 0
        for key, value in sort_dic.items():
            ratio = value[1] / self.total_count
            if ratio >= 0.01:
                sub_dict[key] = round(ratio, 4)
                count_top_city += value[1]
            if len(sub_dict) == 10:
                other_ratio = 1 - count_top_city / self.total_count
                sub_dict["Другие"] = round(other_ratio, 4)
                break
        return sub_dict


class DictByYear:
    """
    Словарь для формирования статистики по годам
    Atributes
    ---------
    data-dict: dict [int, [int, int]]
        данные словаря
    """

    def __init__(self):
        """
        Инициализация обьекта, создание пустого словаря
        """
        self.data_dict = {}

    def add_data(self, year, value, count):
        """
        Добавляет элемент в словарь
        :param year: int
            год
        :param value: float
            средний оклад
        :param count: int
            количество вакансий (0 или 1)
        """
        if year not in self.data_dict.keys():
            self.data_dict[year] = [value, count]
        else:
            self.data_dict[year][0] += value
            self.data_dict[year][1] += count

    def get_by_salary(self):
        """
        :return: dict[int, int]
            данные в виде: год - средняя зарплата

        >>> t = DictByYear()
        >>> t.data_dict = {1: [120000, 3], 2: [60000, 1], 3: [90000, 4], 4: [280000, 20]}
        >>> t.get_by_salary()
        {1: 40000, 2: 60000, 3: 22500, 4: 14000}

        >>> t = DictByYear()
        >>> t.data_dict = {1: [120000, 7], 2: [60000, 1], 3: [90000, 13], 4: [280000, 17]}
        >>> t.get_by_salary()
        {1: 17142, 2: 60000, 3: 6923, 4: 16470}

        >>> t = DictByYear()
        >>> t.data_dict = {3: [120000, 3], 8: [0, 0], 2: [900000, 15], 1: [0, 20], 5: [1000000, 10], 6: [5000000, 0], 7: [2800000, 14], 4: [1000000, 10], 13: [420000, 7], 15: [580000, 9], 11: [400000, 4], 12: [280000, 4], 9: [531000, 15]}
        >>> t.get_by_salary()
        {3: 40000, 8: 0, 2: 60000, 1: 0, 5: 100000, 6: 0, 7: 200000, 4: 100000, 13: 60000, 15: 64444, 11: 100000, 12: 70000, 9: 35400}

        >>> t = DictByYear()
        >>> t.get_by_salary()
        {}
        """
        sub_dict = {}
        for key, value in self.data_dict.items():
            sub_dict[key] = int(value[0] // value[1]) if value[1] != 0 else 0
        return sub_dict

    def get_by_count(self):
        """
        :return: dict[int, int]
            данные в виде: год - количество вакансий

        >>> t = DictByYear()
        >>> t.data_dict = {1: [120000, 7], 2: [60000, 1], 3: [90000, 13], 4: [280000, 17]}
        >>> t.get_by_count()
        {1: 7, 2: 1, 3: 13, 4: 17}

        >>> t = DictByYear()
        >>> t.data_dict = {3: [120000, 3], 8: [0, 0], 2: [900000, 15], 1: [0, 20], 5: [1000000, 10], 6: [5000000, 0], 7: [2800000, 14], 4: [1000000, 10], 13: [420000, 7], 15: [580000, 9], 11: [400000, 4], 12: [280000, 4], 9: [531000, 15]}
        >>> t.get_by_count()
        {3: 3, 8: 0, 2: 15, 1: 20, 5: 10, 6: 0, 7: 14, 4: 10, 13: 7, 15: 9, 11: 4, 12: 4, 9: 15}

        >>> t = DictByYear()
        >>> t.get_by_count()
        {}
        """
        sub_dict = {}
        for key, value in self.data_dict.items():
            sub_dict[key] = value[1]
        return sub_dict


class DataSet:
    """
    Класс для хранения данных и их статистической обработке

    Atribures
    ---------
    file_name : str
        имя/полный путь файла
    vacancies_objects : Vacancy[]
        массив вакансий
    salary_count_by_year : DictByYear
        зарплата и кол-во вакансий по годам
    job_salary_count_by_year : DictByYear
        зарплата и кол-во вакансий по годам для выбранной профессии
    salary_count_by_city : DictByCity
        зарплата и кол-во вакансий по городам
    """

    def __init__(self, file_name):
        """
        Инициализация обьекта
        :param file_name: str
            имя/полный путь файла
        """
        self.file_name = file_name
        self.vacancies_objects = DataSet._set_vacancies(*DataSet._csv_reader(file_name))

        self.salary_count_by_year = DictByYear()
        self.job_salary_count_by_year = DictByYear()
        self.salary_count_by_city = DictByCity()

    @staticmethod
    def _csv_reader(file_name):
        """
        Считывает данные с csv файла
        :param file_name: str
            имя/полный путь файла
        :return: (str[], str[])
            заглавия(параметры), значения(сами вакансии)
        """
        file_csv = csv.reader(open(file_name, encoding='utf_8_sig'))
        list_data = [x for x in file_csv if x.count('') == 0]

        return list_data[0], list_data[1:]

    @staticmethod
    def _set_vacancies(headers, vacancies):
        """
        Создаёт массив вакансий
        :param headers: str[]
            заглавия
        :param vacancies: str[]
            вакансии
        :return: Vacancy[]
            массив вакансий
        """
        list_vacancies = []
        for vac in vacancies:
            dic = {}
            for i, item in enumerate(headers):
                dic[item] = vac[i]
            list_vacancies.append(
                Vacancy(dic['name'], dic['salary_from'], dic['salary_to'], dic['salary_currency'], dic['area_name'],
                        dic['published_at']))

        return list_vacancies

    def collect_statistic(self, profession):
        """
        Формирует статистику
        :param profession: str
            навзвание профессии

        >>> t = DataSet('test.csv')
        >>> t.collect_statistic('аналитик')
        >>> t.salary_count_by_year.data_dict
        {2007: [800750.0, 18], 2011: [1047000.0, 19], 2013: [738900.0, 19]}
        >>> t.job_salary_count_by_year.data_dict
        {2007: [125000.0, 2], 2011: [0, 0], 2013: [49000.0, 1]}
        >>> t.salary_count_by_city.data_dict
        {'Санкт-Петербург': [224000.0, 6], 'Москва': [1594150.0, 31], 'Саратов': [7500.0, 1], 'Екатеринбург': [175000.0, 4], 'Новосибирск': [45000.0, 1], 'Другие регионы': [60000.0, 1], 'Зеленоград': [80000.0, 1], 'Верхне-Приволжский округ': [18000.0, 1], 'Раменское': [55000.0, 1], 'Воронеж': [20000.0, 1], 'Пермь': [169000.0, 3], 'Ярославль': [17500.0, 1], 'Ижевск': [20000.0, 1], 'Владивосток': [60000.0, 1], 'Курган': [14000.0, 1], 'Томск': [27500.0, 1]}
        """
        for vac in self.vacancies_objects:
            self.salary_count_by_year.add_data(vac.published_at.year, vac.average_salary, 1)
            if profession in vac.name:
                self.job_salary_count_by_year.add_data(vac.published_at.year, vac.average_salary, 1)
            else:
                self.job_salary_count_by_year.add_data(vac.published_at.year, 0, 0)
            self.salary_count_by_city.add_data(vac.area_name, vac.average_salary)

    def get_statistic(self):
        """
        Выдает статистические данные в виде: зп по годам, вакансии по годам,
            зп по годам для профессии, вакансии по годам для професии,
            зп по городам, вакансии по городам

        :return: (dict[int, int], dict[int, int], dict[int, int], dict[int, int], dict[str, int], dict[str, int])
        """
        return self.salary_count_by_year.get_by_salary(), \
               self.salary_count_by_year.get_by_count(), \
               self.job_salary_count_by_year.get_by_salary(), \
               self.job_salary_count_by_year.get_by_count(), \
               self.salary_count_by_city.get_by_salary(), \
               self.salary_count_by_city.get_by_count()

    def print_statistic(self):
        """
        Вывод статисических данных
        """
        print(f"Динамика уровня зарплат по годам: {self.salary_count_by_year.get_by_salary()}")
        print(f"Динамика количества вакансий по годам: {self.salary_count_by_year.get_by_count()}")
        print(
            f"Динамика уровня зарплат по годам для выбранной профессии: {self.job_salary_count_by_year.get_by_salary()}")
        print(
            f"Динамика количества вакансий по годам для выбранной профессии: {self.job_salary_count_by_year.get_by_count()}")
        print(f"Уровень зарплат по городам (в порядке убывания): {self.salary_count_by_city.get_by_salary()}")
        print(
            f"Доля вакансий по городам (в порядке убывания): {dict(list(self.salary_count_by_city.get_by_count().items())[:10])}")


class Vacancy:
    """
    Класс для описания вакансии
    Atributes
    ---------
    name : str
        название вакансии
    average_salary : float
        средняя зарплата в рублях
    area_name : str
        название региона
    published_at : datetime
        дата публикации
    _currency_to_rub : dict[str, float | int]
        словарь для перевода в рубли
    """
    _currency_to_rub = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
    }

    def __init__(self, name, salary_from, salary_to, salary_currency, area_name, published_at):
        """
        Инициализация обьекта
        :param name: str
            название вакансии
        :param salary_from: str
            нижняя граница оклада
        :param salary_to: str
            верхняя граница оклада
        :param salary_currency: str
            валюта
        :param area_name: str
            название региона
        :param published_at: str
            дата публикации
        """
        self.name = name
        self.average_salary = (float(salary_from) + float(salary_to)) / 2 * Vacancy._currency_to_rub[
            salary_currency]
        self.area_name = area_name
        self.published_at = ".".join(reversed(published_at[:10].split("-")))
        # res_data = datetime.strptime(data, "%Y-%m-%dT%H:%M:%S%z")
        # f"{res_data.day}.{res_data.month:02}.{res_data.year}"

        # datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z")


class Report:
    """
    Класс для формирования отчёта
    Atributes
    ---------
    profession : str
        профессия
    salary_by_year : dict[int, int]
        зп по годам
    count_by_year : dict[int, int]
        кол-во вакансий по годам
    profession_salary_by_year : dict[int, int]
        зп по годам для профессии
    profession_count_by_year : dict[int, int]
        кол-во вакансий по годам для профессии
    salary_by_city : dict[str, int]
        зп по городам
    count_by_city : dict[str, int]
        кол-во вакансий по городам
    """

    def __init__(self, salary_by_year, count_by_year, job_salary_by_year, job_count_by_year,
                 salary_by_city, count_by_city, prof):
        """
        Инициализация обьекта
        :param salary_by_year: dict[int, int]
            зп по годам
        :param count_by_year: dict[int, int]
            кол-во вакансий по годам
        :param job_salary_by_year: dict[int, int]
            зп по годам для профессии
        :param job_count_by_year: dict[int, int]
            кол-во вакансий по годам для профессии
        :param salary_by_city: dict[str, int]
            зп по городам
        :param count_by_city: dict[str, int]
            кол-во вакансий по городам
        :param prof: str
            профессия
        """
        self.profession = prof
        self.salary_by_year = salary_by_year
        self.count_by_year = count_by_year
        self.profession_salary_by_year = job_salary_by_year
        self.profession_count_by_year = job_count_by_year
        self.salary_by_city = salary_by_city
        self.count_by_city = count_by_city

    def generate_image(self):
        """
        Генерирует png файл с графиками
        """
        fig, ax = plt.subplots(2, 2)
        self._create_first_graph(ax[0, 0])
        self._create_second_graph(ax[0, 1])
        self._create_third_graph(ax[1, 0])
        self._create_fourth_graph(ax[1, 1])
        plt.tight_layout()
        plt.savefig("graph.png")
        plt.show()

    def _create_first_graph(self, ax):
        """
        Генерирует диграмму: уровень зарплат по годам как общий, так и для выбранной профессии
        :param ax: Any
            место для отрисовки графика
        """
        ax.set_title("Уровень зарплат по годам")
        w = 0.4
        ax.bar([val - w / 2 for val in range(len(self.salary_by_year.keys()))], self.salary_by_year.values(), width=w,
               label="средняя з/п")
        ax.bar([val + w / 2 for val in range(len(self.salary_by_year.keys()))],
               self.profession_salary_by_year.values(), width=w, label=f"з/п {self.profession}")
        ax.set_xticks(range(self.salary_by_year.__len__()), self.salary_by_year.keys(), rotation="vertical")
        ax.tick_params(axis="both", labelsize=8)
        ax.legend(fontsize=8)
        ax.yaxis.set_major_locator(IndexLocator(base=10000, offset=0))

    def _create_second_graph(self, ax):
        """
        Генерирует диграмму: количество вакансий по годам как общий, так и для выбранной профессии
        :param ax: Any
            место для отрисовки графика
        """
        ax.set_title("Количество ваканский по годам")
        w = 0.4
        ax.bar([val - w / 2 for val in range(len(self.count_by_year))], self.count_by_year.values(), width=w,
               label="Количество ваканксий")
        ax.bar([val + w / 2 for val in range(len(self.count_by_year))],
               self.profession_count_by_year.values(), width=w, label=f"Количество ваканксий\n{self.profession}")
        ax.set_xticks(range(len(self.count_by_year)), self.count_by_year.keys(), rotation="vertical")
        ax.tick_params(axis="both", labelsize=8)
        ax.legend(fontsize=8, loc='upper left')

    def _create_third_graph(self, ax):
        """
        Генерирует горизонтальну диграмму: уровень зарплат по городам
        :param ax: Any
            место для отрисовки графика
        """
        ax.set_title("Уровень зарплат по городам")
        y_pos = range(len(self.salary_by_city))
        cities = [re.sub(r"[- ]", "\n", c) for c in self.salary_by_city.keys()]
        ax.barh(y_pos, self.salary_by_city.values())
        ax.set_yticks(y_pos, cities)
        ax.invert_yaxis()
        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=6)

    def _create_fourth_graph(self, ax):
        """
        Генерирует круговую диграмму: уколичество вакансий по городам
        :param ax: Any
            место для отрисовки графика
        """
        ax.set_title("Доля вакансий по городам")
        sort_dic = dict(sorted(self.count_by_city.items(), key=lambda item: item[1], reverse=True))
        ax.pie(sort_dic.values(), labels=sort_dic.keys(), textprops={'fontsize': 6})

    def generate_pdf(self):
        """
        Формирует pdf файл со статистикой в виде таблиц и диаграмм
        """
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("pdf_template.html")

        heads_years = ["Год", "Средняя зарплата", f"Средняя зарплата - {self.profession}", "Количество вакансий",
                       f"Количество вакансий - {self.profession}"]
        heads_cities = ["Город", "Уровень зарплат", "Город", "Доля вакансий"]

        formatted_dict = dict([(k, f"{v:.2%}") for k, v in list(self.count_by_city.items())[:10]])

        pdf_template = template.render(
            {"profession": self.profession, "salary_by_year": self.salary_by_year, "count_by_year": self.count_by_year,
             "profession_salary_by_year": self.profession_salary_by_year,
             "profession_count_by_year": self.profession_count_by_year,
             "salary_by_city": self.salary_by_city,
             "count_by_city": formatted_dict,
             "heads_years": heads_years,
             "heads_cities": heads_cities})
        config = pdfkit.configuration(wkhtmltopdf=r'D:\Проги\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options={"enable-local-file-access": None})


def get_statistic():
    """
    Запускает процесс для формирования отчёта по статистике
    :return: формирует pdf файл со статистикой по вакансиям
    """
    file_name = input('Введите название файла: ')
    profession = input('Введите название профессии: ')
    data = DataSet(file_name)
    data.collect_statistic(profession)
    data.print_statistic()

    rep = Report(*data.get_statistic(), profession)
    rep.generate_image()
    rep.generate_pdf()


# get_statistic()

if __name__ == "__main__":
    import doctest

    doctest.testmod()
