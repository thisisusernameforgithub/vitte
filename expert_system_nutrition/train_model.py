# -*- coding: utf-8 -*-

# Cкрипт создания, обучения и сохранения модели. классификации рациона

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os


def train_and_evaluate():
    # процесс обучения модели на основе файла датасета ration_dataset.csv
    dataset_path = os.path.join(os.path.dirname(__file__), "ration_dataset.csv")

    if not os.path.exists(dataset_path):
        print(f"Ошибка: файл {dataset_path} не найден")
        return

    print(f"Загрузка набора данных из {dataset_path} ...")
    df = pd.read_csv(dataset_path)

    X = df.drop("label", axis=1)
    y = df["label"]

    # разделение данных на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n### Сравнение алгоритмов машинного обучения ###")

    model_candidates = {
        "RandomForest": RandomForestClassifier(
            n_estimators=100, max_depth=12, random_state=42
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=50, random_state=42
        ),
        "LinearSVM": SVC(kernel="linear", C=1.0, probability=True, random_state=42),
    }

    best_model = None
    best_score = 0
    best_model_name = ""

    for name, model in model_candidates.items():
        print(f"Тестирование модели {name} ...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"  Accuracy: {acc:.4f}")

        if acc > best_score:
            best_score = acc
            best_model = model
            best_model_name = name

    print(f"\nФинальный выбр: {best_model_name} (Accuracy: {best_score:.4f})")

    # сохранение модели
    model_path = os.path.join(os.path.dirname(__file__), "model.joblib")
    joblib.dump(best_model, model_path)
    print(f"Модель сохранена в {model_path}")

    # детальный отчет
    y_pred = best_model.predict(X_test)
    print("\nОтчет о классификации:")
    print(classification_report(y_test, y_pred))


if __name__ == "__main__":
    try:
        train_and_evaluate()
        print("\nОбучение интеллектуального модуля завершено")
    except Exception as e:
        print(f"\nОшибка при обучении: {e}")
