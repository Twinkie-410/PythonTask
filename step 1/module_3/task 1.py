import pandas as pd

pd.set_option("display.max_columns", False)
pd.set_option("expand_frame_repr", False)


def section_by_year(file_path="..\\..\\Data\\vacancies_by_year.csv"):
    """
    Разделяет входной файл на более мелкие, группирую по годам
    :param file_path: str
    """
    df = pd.read_csv(file_path)
    df["year"] = df["published_at"].apply(lambda s: s[:4])
    df = df.groupby("year")
    for year, data in df:
        data[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]].to_csv(
            rf"csv_files\part_{year}.csv", index=False)


section_by_year()
