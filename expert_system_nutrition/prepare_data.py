# -*- coding: utf-8 -*-

# Скрипт для автоматической подготовки датасета (конвертация xlsx в csv)

import pandas as pd
import zipfile
import os

ZIP_FILE = "archive.zip"
XLSX_FILE = "ABBREV_with_CLASS.xlsx"
CSV_FILE = "ABBREV_with_CLASS.csv"


def main():
    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extract(XLSX_FILE)
    df = pd.read_excel(XLSX_FILE)
    df.to_csv(CSV_FILE, sep=";", index=False)

    os.remove(XLSX_FILE)


if __name__ == "__main__":
    main()
