# -*- coding: utf-8 -*-

# Модуль интеллектуальной оценки рациона на базе обученной ML-модели

import os
import joblib
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RationEvaluator:
    def __init__(self, model_path=None):
        if model_path is None:
            self.model_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "model.joblib",
            )
        else:
            self.model_path = model_path

        self.model = None
        self.version = "1.1.0"
        self.features = ["calories", "protein", "fat", "carbs"]

        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            logger.error(f"Файл модели не найден по пути: {self.model_path}")
            return False

        try:
            self.model = joblib.load(self.model_path)
            logger.info(
                f"Интеллектуальный модуль (v{self.version}) успешно инициализирован"
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка при загрузке бинарного файла модели: {e}")
            return False

    def is_ready(self):
        if self.model is None:

            return self._load_model()
        return True

    def validate_input(self, data):

        # валидация входных данных (КБЖУ)

        if not isinstance(data, dict):
            logger.error("Входные данные должны быть словарем")
            return False

        for feature in self.features:
            if feature not in data:
                logger.warning(
                    f"Входной вектор не полон. Отсутствует признак: {feature}"
                )
                return False
            if not isinstance(data[feature], (int, float)):
                logger.warning(
                    f"Некорректный тип данных для признака {feature}: {type(data[feature])}"
                )
                return False
            if data[feature] < 0:
                logger.warning(f"Отрицательное значение для {feature} недопустимо")
                return False
        return True

    def predict(self, daily_totals):
        # классификация рациона на основе суммарных нутриентов
        if not self.is_ready():
            return "Ошибка: интеллектуальный модуль временно недоступен (модель не загружена)"

        if not self.validate_input(daily_totals):
            return "Ошибка: некорректные или неполные данные для экспертного анализа"

        try:
            input_df = pd.DataFrame([daily_totals], columns=self.features)

            # предсказание
            prediction_array = self.model.predict(input_df)
            result = str(prediction_array[0])

            logger.info(f"Экспертное решение для КБЖУ {daily_totals}: {result}")

            return result

        except Exception as e:
            logger.error(f"Ошибка при выполнении математического предсказания: {e}")
            return "Ошибка при обработке данных в экспертном модуле"

    def get_feature_importance(self):
        if self.model and hasattr(self.model, "feature_importances_"):
            return dict(zip(self.features, self.model.feature_importances_))
        return None

    def __repr__(self):
        return f"<RationEvaluator v{self.version} Ready={self.is_ready()}>"
