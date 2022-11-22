import csv
import datetime
import re
import matplotlib.pyplot as plt
import pdfkit
from matplotlib.ticker import IndexLocator
from jinja2 import Environment, FileSystemLoader


class DictByCity:
    def __init__(self):
        self.data_dict = {}
        self.total_count = 0

    def add_data(self, city, value):
        if city not in self.data_dict.keys():
            self.data_dict[city] = [value, 1]
        else:
            self.data_dict[city][0] += value
            self.data_dict[city][1] += 1
        self.total_count += 1

    def get_by_salary(self):
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
    def __init__(self):
        self.data_dict = {}

    def add_data(self, year, value, count):
        if year not in self.data_dict.keys():
            self.data_dict[year] = [value, count]
        else:
            self.data_dict[year][0] += value
            self.data_dict[year][1] += count

    def get_by_salary(self):
        sub_dict = {}
        for key, value in self.data_dict.items():
            sub_dict[key] = int(value[0] // value[1]) if value[1] != 0 else 0
        return sub_dict

    def get_by_count(self):
        sub_dict = {}
        for key, value in self.data_dict.items():
            sub_dict[key] = value[1]
        return sub_dict


class DataSet:
    def __init__(self, file_name):
        self.file_name = file_name
        self.vacancies_objects = DataSet._set_vacancies(*DataSet._csv_reader(file_name))

        self.salary_count_by_year = DictByYear()
        self.job_salary_count_by_year = DictByYear()
        self.salary_count_by_city = DictByCity()

    @staticmethod
    def _csv_reader(file_name):
        file_csv = csv.reader(open(file_name, encoding='utf_8_sig'))
        list_data = [x for x in file_csv if x.count('') == 0]

        return list_data[0], list_data[1:]

    @staticmethod
    def _set_vacancies(headers, vacancies):
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
        for vac in self.vacancies_objects:
            self.salary_count_by_year.add_data(vac.published_at.year, vac.average_salary, 1)
            if profession in vac.name:
                self.job_salary_count_by_year.add_data(vac.published_at.year, vac.average_salary, 1)
            else:
                self.job_salary_count_by_year.add_data(vac.published_at.year, 0, 0)
            self.salary_count_by_city.add_data(vac.area_name, vac.average_salary)

    def get_statistic(self):
        return self.salary_count_by_year.get_by_salary(), \
               self.salary_count_by_year.get_by_count(), \
               self.job_salary_count_by_year.get_by_salary(), \
               self.job_salary_count_by_year.get_by_count(), \
               self.salary_count_by_city.get_by_salary(), \
               self.salary_count_by_city.get_by_count()

    def print_statistic(self):
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
        self.name = name
        self.average_salary = (float(salary_from) + float(salary_to)) / 2 * Vacancy._currency_to_rub[
            salary_currency]
        self.area_name = area_name
        self.published_at = datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z")


class Report:
    def __init__(self, salary_by_year, count_by_year, job_salary_by_year, job_count_by_year,
                 salary_by_city, count_by_city, prof):
        self.profession = prof
        self.salary_by_year = salary_by_year
        self.count_by_year = count_by_year
        self.profession_salary_by_year = job_salary_by_year
        self.profession_count_by_year = job_count_by_year
        self.salary_by_city = salary_by_city
        self.count_by_city = count_by_city

    def generate_image(self):
        fig, ax = plt.subplots(2, 2)
        self._create_first_graph(ax[0, 0])
        self._create_second_graph(ax[0, 1])
        self._create_third_graph(ax[1, 0])
        self._create_fourth_graph(ax[1, 1])
        plt.tight_layout()
        plt.savefig("graph.png")
        plt.show()

    def _create_first_graph(self, ax):
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
        ax.set_title("Уровень зарплат по городам")
        y_pos = range(len(self.salary_by_city))
        cities = [re.sub(r"[- ]", "\n", c) for c in self.salary_by_city.keys()]
        ax.barh(y_pos, self.salary_by_city.values())
        ax.set_yticks(y_pos, cities)
        ax.invert_yaxis()
        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=6)

    def _create_fourth_graph(self, ax):
        ax.set_title("Доля вакансий по городам")
        sort_dic = dict(sorted(self.count_by_city.items(), key=lambda item: item[1], reverse=True))
        ax.pie(sort_dic.values(), labels=sort_dic.keys(), textprops={'fontsize': 6})

    def generate_pdf(self):
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


file_name = input('Введите название файла: ')
profession = input('Введите название профессии: ')
data = DataSet(file_name)
data.collect_statistic(profession)
data.print_statistic()

rep = Report(*data.get_statistic(), profession)
rep.generate_image()
rep.generate_pdf()
