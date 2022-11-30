from prettytable import PrettyTable
import csv
import re
import datetime

# region service
# region dictionaries
title = {
    'name': 'Название',
    'description': 'Описание',
    'key_skills': 'Навыки',
    'experience_id': 'Опыт работы',
    'premium': 'Премиум-вакансия',
    'employer_name': 'Компания',
    'salary_from': 'Нижняя граница вилки оклада',
    'salary_to': 'Верхняя граница вилки оклада',
    'salary_gross': 'Оклад указан до вычета налогов',
    'salary_currency': 'Идентификатор валюты оклада',
    'area_name': 'Название региона',
    'published_at': 'Дата публикации вакансии',
}
currency = {
    "AZN": "Манаты",
    "BYR": "Белорусские рубли",
    "EUR": "Евро",
    "GEL": "Грузинский лари",
    "KGS": "Киргизский сом",
    "KZT": "Тенге",
    "RUR": "Рубли",
    "UAH": "Гривны",
    "USD": "Доллары",
    "UZS": "Узбекский сум"
}
work_experience = {
    "noExperience": "Нет опыта",
    "between1And3": "От 1 года до 3 лет",
    "between3And6": "От 3 до 6 лет",
    "moreThan6": "Более 6 лет"
}
salary_gross = {
    'True': 'Без вычета налогов',
    'False': 'С вычетом налогов'
}
true_false_dic = {
    'True': 'Да',
    'False': 'Нет'
}
cast_to_bool_dic = {
    'Да': True,
    'Нет': False
}

weight_for_work_experience = {
    "noExperience": 0,
    "between1And3": 1,
    "between3And6": 2,
    "moreThan6": 3
}

# endregion
dictionaries = [title, currency, work_experience, salary_gross, true_false_dic]


def exit_with_print_message(exit_message=''):
    """
    Досрочно прекращает работу приложения и выводит сообщение в консоль
    :param exit_message: str
        сообщение
    """
    print(exit_message)
    exit()


# endregion


class DataSet:
    """
    Вакансии и название файла
    Atribute
    --------
    file_name : str
        имя/полный путь файла
    vacancies_object : Vacancy[]
        список вакансий
    """
    def __init__(self, file_name):
        """
        Инициализация обьекта
        :param file_name: str
            имя/полный путь файла
        """
        self.file_name = file_name
        self.vacancies_objects = DataSet._set_vacancies(*DataSet._csv_reader(file_name))

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
                dic[item] = DataSet._clean_string(vac[i], i == 2)
            list_vacancies.append(Vacancy(dic['name'],
                                          dic['description'],
                                          dic['key_skills'].split('\n'),
                                          dic['experience_id'],
                                          dic['premium'],
                                          dic['employer_name'],
                                          Salary(dic['salary_from'],
                                                 dic['salary_to'],
                                                 dic['salary_gross'],
                                                 dic['salary_currency']),
                                          dic['area_name'],
                                          dic['published_at']))

        return list_vacancies

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
        list_data = [x for x in file_csv]
        if len(list_data) == 1:
            exit_with_print_message('Нет данных')
        if len(list_data) == 0:
            exit_with_print_message('Пустой файл')
        titles = list_data[0]
        values = [x for x in list_data[1:] if x.count('') == 0 and len(x) == len(titles)]

        return titles, values

    @staticmethod
    def _clean_string(string, is_skills):
        """
        Удаляет html теги и лишние пробелы из строки
        :param string: str
            строка для обработки
        :param is_skills: bool
            являеется ли строка набором навыков
        :return: str
            преобразованная строка
        """
        string = re.sub(r'<[^>]*>', '', string)
        string = ' '.join(string.split(' ')) if is_skills else ' '.join(string.split())
        return string

    @staticmethod
    def translate(word, dictionaries=[title], reverse=False):
        """
        Перевод слов
        :param word: str
            слово
        :param dictionaries: dict[str, str]
            словарь для перевода
        :param reverse: bool
            True: рус -> англ, False: англ -> рус
        :return: str
            результат перевеода, если не удалось - возвращает исходное слово
        """
        result = word
        for dic in dictionaries:
            d = dict([(value, key) for key, value in dic.items()]) if reverse else dic
            result = d[word] if word in d.keys() else result
        return result

    def filter_data(self, filter_parameters):
        """
        Филтрация вакансий по параметру
        :param filter_parameters: str
            парметр филтрации вида: параметр: значение параметра
        :return: оставляет только вакансии, удовлетваряющие фильтру
        """
        if filter_parameters == '':
            return
        field, value = (DataSet.translate(w, dictionaries, True) for w in filter_parameters.split(': '))
        filter_data = []
        for vac in self.vacancies_objects:
            if DataSet._filter_vacancy(vac, field, value):
                filter_data.append(vac)
        if len(filter_data) != 0:
            self.vacancies_objects = filter_data
        else:
            exit_with_print_message('Ничего не найдено')

    @staticmethod
    def _filter_vacancy(vac, filter_field, filter_value):
        """
        Проверка, удовлетворяет ли вакансия фильтру
        :param vac: Vacancy
            вакансися
        :param filter_field: str
             параметр фильтрации
        :param filter_value: str
            значение параметра фильтрации
        :return: bool
        """

        if filter_field == 'Оклад':
            return float(vac.salary.salary_from) <= float(filter_value) <= float(vac.salary.salary_to)
        if filter_field == 'salary_currency' or filter_value == 'salary_gross':
            return vac.salary.__getattribute__(filter_field) == filter_value
        if filter_field == 'key_skills':
            for skill in filter_value.split(', '):
                if skill not in vac.key_skills:
                    return False
            return True
        if filter_field == 'published_at':
            return datetime.datetime.strptime(vac.published_at, "%Y-%m-%dT%H:%M:%S%z").strftime(
                "%d.%m.%Y") == filter_value
        return vac.__getattribute__(filter_field) == filter_value

    def sort_data(self, sort_parameter, is_reverse):
        """
        Сортировка вакансий по параметру
        :param sort_parameter: str
            параметр сортировки
        :param is_reverse: str
            восходящий порядок сортировки (да/нет)
        :return: сортирует лист вакансий
        """
        if sort_parameter == '':
            return
        sort_parameter = DataSet.translate(sort_parameter, reverse=True)
        is_reverse = cast_to_bool_dic[is_reverse] if is_reverse in cast_to_bool_dic.keys() else bool(is_reverse)
        if sort_parameter == 'Оклад':
            self.vacancies_objects.sort(key=lambda vac: vac.salary.get_average_salary_in_rubles(),
                                        reverse=is_reverse)
            return
        if sort_parameter == 'key_skills':
            self.vacancies_objects.sort(key=lambda vac: len(vac.key_skills),
                                        reverse=is_reverse)
            return
        if sort_parameter == 'published_at':
            self.vacancies_objects.sort(
                key=lambda vac: datetime.datetime.strptime(vac.published_at, "%Y-%m-%dT%H:%M:%S%z"),
                reverse=is_reverse)
            return
        if sort_parameter == 'experience_id':
            self.vacancies_objects.sort(key=lambda vac: weight_for_work_experience[vac.experience_id],
                                        reverse=is_reverse)
            return
        self.vacancies_objects.sort(key=lambda vac: vac.__getattribute__(sort_parameter), reverse=is_reverse)


class Vacancy:
    """
    Класс для описания вакансии

    Atributes
    ---------
    name : str
        название професии
    description : str
        описание
    key_skills : str[]
        навыки
    experience_id : str
        опыт работы
    premium : str
        премиум вакансия
    employer_name : str
        название компания
    salary : Salary
        зарплата
    area_name : str
        название региона
    published_at : str
        дата публикации
    """
    def __init__(self, name, description, key_skills, experience_id, premium, employer_name, salary, area_name,
                 published_at):
        """
        Инициализация обьекта
        :param name: str
        :param description: str
        :param key_skills: str[]
        :param experience_id: str
        :param premium: str
        :param employer_name: str
        :param salary: Salary
        :param area_name: str
        :param published_at: str
        """
        self.name = name
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = premium
        self.employer_name = employer_name
        self.salary = salary
        self.area_name = area_name
        self.published_at = published_at

    def formatter(self):
        """
        :return: переводит поля опыта работы и прмиаотной вакансии, форматирует дату в виде: Д.М.Г
        """
        self.experience_id = work_experience[self.experience_id]
        self.premium = true_false_dic[self.premium]
        self.published_at = datetime.datetime.strptime(self.published_at, "%Y-%m-%dT%H:%M:%S%z").strftime("%d.%m.%Y")


class Salary:
    """
    Класс для описания зарплаты

    Atributes
    ---------
    salary_from : str
        нижняя граница зп
    salary_to : str
        верхняя граница зп
    salary_gross : str
        до/после вычета налогов
    salary_currency : str
        валюта
    salary_from_rub : float
        нижняя граница зп в рублях
    salary_to_rub : float
        верхняя граница зп в рублях
    _currency_to_rub : dict[str, float | int]
        словарь для конвертации валют
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

    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        """
        Инициализация обьекта
        :param salary_from: str
            нижняя граница зп
        :param salary_to: str
            верхняя граница зп
        :param salary_gross: str
            до/после вычета налогов
        :param salary_currency: str
            валюта
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency
        self.salary_from_rub = float(self.salary_from) * Salary._currency_to_rub[self.salary_currency]
        self.salary_to_rub = float(self.salary_to) * Salary._currency_to_rub[self.salary_currency]

    def get_average_salary_in_rubles(self):
        """
        :return: float
            среднее значение оклада: (нижняя граница оклада + верхняя граница оклада) / 2
        """
        return (self.salary_from_rub + self.salary_to_rub) / 2

    def get_formatted_info(self):
        """
        Разделяет пробелом каждое число по три знака
        :return: str
            строка вида: нижн.гран оклада - верхн.гран. оклада (валюта) (до/после вычета налогов)
        """
        separator_by_thousand = lambda number: '{:,}'.format(int(float(number))).replace(',', ' ')
        return f'{separator_by_thousand(self.salary_from)} - {separator_by_thousand(self.salary_to)} ' \
               f'({currency[self.salary_currency]}) ({salary_gross[self.salary_gross]})'


class InputConnect:
    """
    Класс для взаимодействия с пользователем и хранения вводимых параметров

    Atributes
    ---------
    file_name : str
        имя/полный путь файла
    filter_parameters : str
        параметр филтрации
    sort_parameter : str
        параметр сортировки
    is_reverse_sort : str
        обратный порядок сортировки (по умолчанию - возрастающий)
    indexes : int[]
        требуемый диапозон вывода вакансий: два числа - диапозон "от - до", одно число - стартовый номер для вывода
    parameters : str[]
        названия столбцов, требуемых для вывода
    """

    def __init__(self):
        """
        Инициализация обекта
        """
        params = InputConnect.get_params()
        self.file_name = params[0]
        self.filter_parameters = params[1]
        self.sort_parameter = params[2]
        self.is_reverse_sort = params[3]
        self.indexes = params[4]
        self.parameters = params[5]

    @staticmethod
    def get_params():
        """
        Запрашивает вводные данные и проверяет корректность ввода параметра филтрации и параметра сортировки
        :return: [str, str, str, str, int[], str[]]
            имя/полный путь файла; параметр фильтрации; параметр сортировки; обратный порядок сортировки (да, нет);
            диапозон вывода вакансий; названия столбцов, требуемых для вывода
        """
        file_name = input('Введите название файла: ')
        filter_parameters = input('Введите параметр фильтрации: ')
        sort_parameters = input('Введите параметр сортировки: ')
        is_reverse_sort = input('Обратный порядок сортировки (Да / Нет): ')
        indexes = [int(x) for x in input('Введите диапазон вывода: ').split()]
        parameters = input('Введите требуемые столбцы: ').split(', ')

        InputConnect._confirm_filter(filter_parameters, [*title.values(), 'Оклад'])
        InputConnect._confirm_sort(sort_parameters, is_reverse_sort,
                                   ['Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания',
                                    'Название региона',
                                    'Дата публикации вакансии', 'Оклад', '№'])

        return file_name, filter_parameters, sort_parameters, is_reverse_sort, indexes, parameters

    @staticmethod
    def _confirm_filter(filter_parameters, possible_fields):
        """
        Проверяет параметр фильтрации на корректность
        :param filter_parameters: str
            параметр фильтрации
        :param possible_fields: str[]
            возможные параметры для фильтрации
        """
        if filter_parameters != '':
            if filter_parameters.count(': ') == 0:
                exit_with_print_message('Формат ввода некорректен')
            field = filter_parameters.split(': ')[0]
            if field not in possible_fields:
                exit_with_print_message('Параметр поиска некорректен')

    @staticmethod
    def _confirm_sort(sort_parameter, is_reverse, possible_fields):
        """
        Проверяет параметры сортировки на корректность
        :param sort_parameter: параметр сортировки
        :param is_reverse: параметр обратной сортировки
        :param possible_fields: возможные параметры сортировки
        """
        if sort_parameter != '':
            if sort_parameter not in possible_fields:
                exit_with_print_message('Параметр сортировки некорректен')
            if is_reverse not in cast_to_bool_dic.keys() and is_reverse != '':
                exit_with_print_message('Порядок сортировки задан некорректно')


class TableData:
    """
    Данные вакансий, оформелнные в виде таблицы

    Atributes
    ---------
    data : Vacancy[]
        маассив вакансий
    table : PrettyTable
        таблица с вакансиями
    """

    def __init__(self, data):
        """
        Инициализация обьекта

        :param data: Vacancy[]
        """
        self.data = data
        self.table = TableData._create_table(data)

    def print(self, indexes, parameters):
        """
        Выводит таблицу с вакансиями

        :param indexes: int[]
            два числа - диапозон "от - до", одно число - стартовый номер для вывода
        :param parameters: str[]
            требуемые столбцы для отображения
        """
        print(self.table.get_string(fields=['№', *parameters] if parameters.count('') == 0 else self.table.field_names,
                                    start=indexes[0] - 1 if len(indexes) >= 1 else 0,
                                    end=indexes[1] - 1 if len(indexes) == 2 else len(self.data)))

    @staticmethod
    def _create_table(data):
        """
        Создаёт таблицу с указанными данными
        :param data: Vacancy[]
        :return: таблица с данными о вакансиях
        """
        result_table = PrettyTable()
        result_table.field_names = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия',
                                    'Компания', 'Оклад', 'Название региона', 'Дата публикации вакансии']
        for i, vac in enumerate(data):
            vac.formatter()
            row = [i + 1]
            for field in result_table.field_names[1:]:
                if field == 'Оклад':
                    row.append(vac.salary.get_formatted_info())
                else:
                    value = vac.__getattribute__(DataSet.translate(field, reverse=True))
                    value = '\n'.join(value) if type(value) == list else value
                    value = value[:100] + '...' if len(value) > 100 else value
                    row.append(value)
            result_table.add_row(row)

        result_table.align = 'l'
        result_table.hrules = 1
        result_table.max_width = 20

        return result_table


def get_table():
    """
    Запускает процесс для создания таблицы вакансий

    :return: Выводит таблицу ASCII с вакансиями
    """
    params = InputConnect()
    data = DataSet(params.file_name)
    data.filter_data(params.filter_parameters)
    data.sort_data(params.sort_parameter, params.is_reverse_sort)
    table = TableData(data.vacancies_objects)
    table.print(params.indexes, params.parameters)
