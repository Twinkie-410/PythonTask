# import pandas as pd
#
# pd.set_option("display.max_columns", False)
# pd.set_option("expand_frame_repr", False)
#
# file = "join_salaries_field_vacancies_full.csv"
# df = pd.read_csv(file, nrows=100)
# df = df.dropna()
# df["year"] = df["published_at"][:4]
# df = df
# print(df)

import multiprocessing
import os
import pandas as pd
import concurrent.futures as con_fut
import pdfkit
from jinja2 import Environment, FileSystemLoader


class Solution:
    def __init__(self, file_path, profession):
        """
        Инициализация объекта

        :param file_path: str
            файл/путь к файлу с данными
        :param profession: str
            требуемая профессия, по которой будет составляться аналитика
        """
        self.file_path = file_path
        self.profession = profession

        self.salary_by_years = {}
        self.count_by_years = {}
        self.prof_salary_by_years = {}
        self.prof_count_by_years = {}

    def divide_file_by_year(self):
        """
        Разделяет входной файл на более мелкие, группирую по годам
        """
        df = pd.read_csv(self.file_path)
        df = df.dropna()
        df["year"] = df["published_at"].apply(lambda s: s[:4])
        df = df.groupby("year")
        for year, data in df:
            data[["name", "salary", "area_name", "published_at"]].to_csv(rf"divided_files_csv\part_{year}.csv",
                                                                         index=False)

    def get_statistic_by_year(self, file_csv):
        """
        Сосавляет статистику по году
        :param file_csv: str
            файл с данными за год
        :return: (str, [int, int, int, int])
            (год, [ср. зп, всего вакансий, ср. зп для профессии, вакансий по профессии])
        """
        df = pd.read_csv(file_csv)
        df["published_at"] = df["published_at"].apply(lambda s: int(s[:4]))
        df_vac = df[df["name"].str.contains(self.profession)]

        return df["published_at"].values[0], [int(df["salary"].mean()), len(df),
                                              int(df_vac["salary"].mean() if len(df_vac) != 0 else 0), len(df_vac)]

    def get_statistic(self):
        """
        Собирает статистику по годам

        Использует несколько процессов для работы
        """
        files = [rf"divided_files_csv\{file_name}" for file_name in os.listdir("divided_files_csv")]
        pool = multiprocessing.Pool(4)
        res_list = pool.starmap(self.get_statistic_by_year, [(file,) for file in files])
        pool.close()

        for year, data_stat in res_list:
            self.salary_by_years[year] = data_stat[0]
            self.count_by_years[year] = data_stat[1]
            self.prof_salary_by_years[year] = data_stat[2]
            self.prof_count_by_years[year] = data_stat[3]

    def print_statistic(self):
        print(f"Динамика уровня зарплат по годам: {self.salary_by_years}")
        print(f"Динамика количества вакансий по годам: {self.count_by_years}")
        print(f"Динамика уровня зарплат по годам для выбранной профессии: {self.prof_salary_by_years}")
        print(f"Динамика количества вакансий по годам для выбранной профессии: {self.prof_count_by_years}")

    def generate_pdf(self):
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("statistic_with_pandas.html")

        heads_years = ["Год", "Средняя зарплата", f"Средняя зарплата - {self.profession}", "Количество вакансий",
                       f"Количество вакансий - {self.profession}"]

        pdf_template = template.render(
            {"profession": self.profession, "salary_by_year": self.salary_by_years,
             "count_by_year": self.count_by_years,
             "profession_salary_by_year": self.prof_salary_by_years,
             "profession_count_by_year": self.prof_count_by_years,
             "heads_years": heads_years, })
        config = pdfkit.configuration(wkhtmltopdf=r'D:\Проги\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'statistic_with_pandas.pdf', configuration=config,
                           options={"enable-local-file-access": None})


if __name__ == '__main__':
    file = input("Введите название файла: ")
    profession = input("Введите название профессии: ")
    solve = Solution(file, profession)
    solve.divide_file_by_year()
    solve.get_statistic()
    solve.generate_pdf()
    # solve.print_statistic()
