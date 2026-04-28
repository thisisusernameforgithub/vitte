# -*- coding: utf-8 -*-

# Модуль для работы с моделью ML

import joblib
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model.joblib")


# модель оценки рациона
class RationEvaluator:
    def __init__(self, model_path=MODEL_PATH):
        try:
            self.model = joblib.load(model_path)
            self.features = ["calories", "protein", "fat", "carbs"]
            print(f"Модель успешно загружена из {model_path}")
        except FileNotFoundError:
            print(
                f"Файл модели не найден по пути {model_path}. убедитесь, что вы запустили train_model.py"
            )
            self.model = None
        except Exception as e:
            print(f"Произошла ошибка при загрузке модели: {e}")
            self.model = None

    # предсказание для суточного набора КБЖУ
    def predict(self, daily_totals):
        if self.model is None:
            return "Ошибка: Модель оценки недоступна."

        try:
            # предсказание
            input_df = pd.DataFrame([daily_totals], columns=self.features)
            prediction = self.model.predict(input_df)
            return prediction[0]

        except Exception as e:
            print(f"Произошла ошибка во время предсказания: {e}")
            return "Ошибка при обработке данных для оценки"


# дебаг - самотестирование (ручной запуск app/ml_model.py)
# if __name__ == "__main__":
#     evaluator = RationEvaluator()
#     if evaluator.model:
#         test_ration = {"calories": 1600, "protein": 80, "fat": 60, "carbs": 180}
#         result = evaluator.predict(test_ration)
#         print(f"рацион 1: {test_ration}")
#         print(f"результат 1: {result}")
#
#         test_ration_2 = {"calories": 2800, "protein": 120, "fat": 90, "carbs": 350}
#         result_2 = evaluator.predict(test_ration_2)
#         print(f"рацион 2: {test_ration_2}")
#         print(f"результат 2: {result_2}")
