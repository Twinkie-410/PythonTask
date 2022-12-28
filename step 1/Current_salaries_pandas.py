import numpy as np
import pandas as pd

pd.set_option("display.max_columns", False)
pd.set_option("expand_frame_repr", False)


def calculate(data, rub_exchange_rate):
    s_from, s_to, cur, date = data
    date = date[:7]
    if pd.isna(cur) or cur not in rub_exchange_rate.columns or (pd.isna(s_from) and pd.isna(s_to)):
        return np.NAN
    salary = s_from if pd.notna(s_from) else 0
    salary += s_to if pd.notna(s_to) else 0
    if salary == 0:
        return np.NAN
    ratio = 1
    if cur != "RUR":
        ratio = rub_exchange_rate[rub_exchange_rate["Date"] == date][cur].values[0]
    return round(salary*ratio)


def join_salaries_field(df_):
    rub_exchange_rate = pd.read_csv("module_3.3_API/currencies.csv")
    df_["salary"] = df_[["salary_from", "salary_to", "salary_currency", "published_at"]].apply(calculate,
                                                                                               rub_exchange_rate=rub_exchange_rate,
                                                                                               axis=1)
    df_ = df_[["name", "salary", "area_name", "published_at"]]
    return df_


file_path = "..\\Data\\vacancies_dif_currencies.csv"
df = pd.read_csv(file_path)
df = df.pipe(join_salaries_field)
df.to_csv("join_salaries_field_vacancies_full.csv", index=False)