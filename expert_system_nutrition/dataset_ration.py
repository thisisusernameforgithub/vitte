# -*- coding: utf-8 -*-

# Скрипт генерации эмпирического набора данных суточных рационов
# генерирует набор данных на основе реальных продуктов из датасета

import pandas as pd
import numpy as np
import os


def generate_realistic_dataset(n_samples=10000, output_file="ration_dataset.csv"):

    csv_path = os.path.join(os.path.dirname(__file__), "ABBREV_with_CLASS.csv")
    if not os.path.exists(csv_path):
        print(f"Ошибка: файл {csv_path} не найден. Сначала запустите prepare_data.py")
        return

    print(f"Загрузка базы продуктов USDA для генерации рационов ...")
    products_df = pd.read_csv(csv_path, sep=";")

    cols_mapping = {
        "Shrt_Desc": "Name",
        "Energ_Kcal": "Calories",
        "Protein_(g)": "Protein",
        "Lipid_Tot_(g)": "Fat",
        "Carbohydrt_(g)": "Carbohydrates",
    }

    products_df = (
        products_df[list(cols_mapping.keys())].rename(columns=cols_mapping).dropna()
    )

    print(f"Генерация {n_samples} реалистичных рационов ...")
    np.random.seed(42)

    data = []
    for i in range(n_samples):
        # генерируем профиль пользователя для расчета индивидуальной нормы
        age = np.random.randint(18, 70)
        weight = np.random.uniform(50, 110)
        height = np.random.uniform(155, 195)
        is_male = np.random.choice([True, False])

        # формула Миффлина-Сан Жеора
        if is_male:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        target_calories = bmr * 1.3

        # сбор рациона из 5-12 случайных продуктов
        n_items = np.random.randint(5, 13)
        sample_items = products_df.sample(n_items)
        weights = np.random.uniform(50, 400, size=n_items)

        total_cal = np.sum((sample_items["Calories"].values / 100) * weights)
        total_prot = np.sum((sample_items["Protein"].values / 100) * weights)
        total_fat = np.sum((sample_items["Fat"].values / 100) * weights)
        total_carb = np.sum((sample_items["Carbohydrates"].values / 100) * weights)

        # разметка
        if total_cal < target_calories * 0.85:
            label = "Дефицит калорий"
        elif total_cal > target_calories * 1.25:
            label = "Избыток калорий"
        else:
            p_perc = (total_prot * 4) / total_cal
            f_perc = (total_fat * 9) / total_cal

            if p_perc < 0.12:
                label = "Недостаток белка"
            elif f_perc > 0.35:
                label = "Избыток жиров"
            elif 0.15 < p_perc < 0.30 and 0.20 < f_perc < 0.35:
                label = "Сбалансированный рацион"
            else:
                label = "Дисбаланс нутриентов"

        data.append([total_cal, total_prot, total_fat, total_carb, label])

        if (i + 1) % 2000 == 0:
            print(f"Создано {i+1} образцов ...")

    df = pd.DataFrame(data, columns=["calories", "protein", "fat", "carbs", "label"])
    df.to_csv(output_file, index=False)
    print(f"Успех! Датасет сохранен в {output_file}. Всего записей: {len(df)}")


if __name__ == "__main__":
    generate_realistic_dataset()
