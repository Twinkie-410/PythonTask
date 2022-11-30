import table
import statistic


def start():
    """
    Запускает процедуру выбора формата данных (таблица вакансий или статистика)

    :return: Выводит таблицу с вакансиями либо формирует отчёт в формате pdf со статистикой
    """
    needed_out = input("Требуемый формат данных: ")
    if needed_out == "Вакансии":
        table.get_table()
    elif needed_out == "Статистика":
        statistic.get_statistic()
    else:
        print("Неккоректный ввод")


start()