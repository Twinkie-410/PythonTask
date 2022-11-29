import table
import statistic


def start():
    needed_out = input("Требуемый формат данных: ")
    if needed_out == "Вакансии":
        table.get_table()
    elif needed_out == "Статистика":
        statistic.get_statistic()
    else:
        print("Неккоректный ввод")


start()
#комментарий в develop