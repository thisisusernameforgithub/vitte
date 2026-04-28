# -*- coding: utf-8 -*-

# Cкрипт создания, обучения и сохранения модели

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# 1. Генерация синтетических данных (т.к. нет ретроспективы)

# сбалансированный класс - "идеал"
IDEAL_CALORIES = 2000  # ккал
IDEAL_PROTEIN = 100  # грамм
IDEAL_FAT = 70  # грамм
IDEAL_CARBS = 245  # грамм

NUM_SAMPLES = 10000

# создание словаря
data = {"calories": [], "protein": [], "fat": [], "carbs": [], "label": []}

# генерация
for _ in range(NUM_SAMPLES):
    ration_type = np.random.randint(0, 3)

    if ration_type == 0:
        calories = np.random.uniform(1000, IDEAL_CALORIES * 0.9 - 1)
        label = "Дефицит калорий"
    elif ration_type == 1:
        calories = np.random.uniform(IDEAL_CALORIES * 0.9, IDEAL_CALORIES * 1.1)
        label = "Сбалансированный рацион"
    else:
        calories = np.random.uniform(IDEAL_CALORIES * 1.1 + 1, 3500)
        label = "Избыток калорий"

    # добавляем шум, чтобы данные выглядели более реалистично.
    protein = max(0, np.random.normal(IDEAL_PROTEIN, 20))
    fat = max(0, np.random.normal(IDEAL_FAT, 15))
    carbs = max(0, np.random.normal(IDEAL_CARBS, 40))

    data["calories"].append(calories)
    data["protein"].append(protein)
    data["fat"].append(fat)
    data["carbs"].append(carbs)
    data["label"].append(label)

# создание DataFrame из словаря
df = pd.DataFrame(data)

# 2. Подготовка данных и обучение модели

# определение признаков (независимых переменных) - КБЖУ
features = ["calories", "protein", "fat", "carbs"]
X = df[features]

# определение целевой переменной
y = df["label"]

# разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# инициализация модели RandomForestClassifier - это ансамбль деревьев решений
model = RandomForestClassifier(n_estimators=100, random_state=42)

# обучение модели
print("Обучение модели ...")
model.fit(X_train, y_train)
print("Модель обучена")

# 3. Оценка модели
# получение предсказаний на тестовой выборке
y_pred = model.predict(X_test)

# расчет точности
accuracy = accuracy_score(y_test, y_pred)
print(f"Точность модели на тестовых данных: {accuracy:.2f}")

# 4. Сохранение модели
model_filename = "model.joblib"
joblib.dump(model, model_filename)

print(f"Модель сохранена в файл {model_filename}")

# проверка
test_input = pd.DataFrame([[2100, 110, 75, 250]], columns=features)
prediction = model.predict(test_input)
print(f"Пример предсказания для {test_input.values.tolist()}: {prediction[0]}")
