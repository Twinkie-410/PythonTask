import multiprocessing
import cProfile
import os
import pandas as pd
import concurrent.futures as con_fut


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
        self.salary_by_cities = {}
        self.count_by_cities = {}

    def divide_file_by_year(self):
        """
        Разделяет входной файл на более мелкие, группирую по годам
        """
        df = pd.read_csv(self.file_path)
        df["year"] = df["published_at"].apply(lambda s: s[:4])
        df = df.groupby("year")
        for year, data in df:
            data[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]].to_csv(
                rf"csv_files\part_{year}.csv", index=False)

    def get_statistic(self):
        self.create_statistic_by_year_mltproc_on()
        self.get_statistic_by_city()

    def get_statistic_by_year(self, file_csv):
        """
        Сосавляет статистику по году
        :param file_csv: str
            файл с данными за год
        :return: (str, [int, int, int, int])
            (год, [ср. зп, всего вакансий, ср. зп для профессии, вакансий по профессии])
        """
        df = pd.read_csv(file_csv)
        df["salary"] = df[["salary_from", "salary_to"]].mean(axis=1)
        df["published_at"] = df["published_at"].apply(lambda s: int(s[:4]))
        df_vac = df[df["name"].str.contains(self.profession)]

        return df["published_at"].values[0], [int(df["salary"].mean()), len(df),
                                              int(df_vac["salary"].mean() if len(df_vac) != 0 else 0), len(df_vac)]

    def create_statistic_by_year_mltproc_off(self):
        """
        Собирает статистику по годам

        Использует только один процесс для работы
        """
        res_list = []
        for filename in os.listdir("csv_files"):
            with open(os.path.join("csv_files", filename), "r") as file_csv:
                res_list.append(self.get_statistic_by_year(file_csv.name))

        for year, data_stat in res_list:
            self.salary_by_years[year] = data_stat[0]
            self.count_by_years[year] = data_stat[1]
            self.prof_salary_by_years[year] = data_stat[2]
            self.prof_count_by_years[year] = data_stat[3]

    def create_statistic_by_year_mltproc_on(self):
        """
        Собирает статистику по годам

        Использует несколько процессов для работы
        """
        files = [rf"csv_files\{file_name}" for file_name in os.listdir("csv_files")]
        pool = multiprocessing.Pool(4)
        res_list = pool.starmap(self.get_statistic_by_year, [(file,) for file in files])
        pool.close()

        for year, data_stat in res_list:
            self.salary_by_years[year] = data_stat[0]
            self.count_by_years[year] = data_stat[1]
            self.prof_salary_by_years[year] = data_stat[2]
            self.prof_count_by_years[year] = data_stat[3]

    def create_statistic_by_year_concurrent_futures(self):
        """
        Собирает статистику по годам

        Использует модуль concurrent futures для работы
        """
        files = [rf"csv_files\{file_name}" for file_name in os.listdir("csv_files")]
        with con_fut.ProcessPoolExecutor(max_workers=4) as executer:
            res = executer.map(self.get_statistic_by_year, files)
        res_list = list(res)

        for year, data_stat in res_list:
            self.salary_by_years[year] = data_stat[0]
            self.count_by_years[year] = data_stat[1]
            self.prof_salary_by_years[year] = data_stat[2]
            self.prof_count_by_years[year] = data_stat[3]

    def get_statistic_by_city(self):
        """
        Собирает статистику по городам
        """
        df = pd.read_csv(self.file_path)
        total = len(df)
        df["salary"] = df[["salary_from", "salary_to"]].mean(axis=1)
        df["count"] = df.groupby("area_name")["area_name"].transform("count")
        df = df[df["count"] > total * 0.01]
        df = df.groupby("area_name", as_index=False)
        df = df[["salary", "count"]].mean().sort_values("salary", ascending=False)
        df["salary"] = df["salary"].apply(lambda s: int(s))

        self.salary_by_cities = dict(zip(df.head(10)["area_name"], df.head(10)["salary"]))

        df = df.sort_values("count", ascending=False)
        df["count"] = round(df["count"] / total, 4)

        self.count_by_cities = dict(zip(df.head(10)["area_name"], df.head(10)["count"]))

    def print_statistic(self):
        print(f"Динамика уровня зарплат по годам: {self.salary_by_years}")
        print(f"Динамика количества вакансий по годам: {self.count_by_years}")
        print(f"Динамика уровня зарплат по годам для выбранной профессии: {self.prof_salary_by_years}")
        print(f"Динамика количества вакансий по годам для выбранной профессии: {self.prof_count_by_years}")
        print(f"Уровень зарплат по городам (в порядке убывания): {self.salary_by_cities}")
        print(f"Доля вакансий по городам (в порядке убывания): {self.count_by_cities}")


if __name__ == '__main__':
    file = input("Введите название файла: ")
    profession = input("Введите название профессии: ")
    solve = Solution(file, profession)
    # solve.divide_file_by_year()
    solve.get_statistic()
    solve.print_statistic()

    # solve = Solution("..\\..\\Data\\vacancies_by_year.csv", "Программист")
    # solve.divide_file_by_year()
    # cProfile.run("solve.create_statistic_by_year_mltproc_on()", sort="cumtime")
    # cProfile.run("solve.create_statistic_by_year_mltproc_off()", sort="cumtime")
    # cProfile.run("solve.create_statistic_by_year_concurrent_futures()", sort="cumtime")
