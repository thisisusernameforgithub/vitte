# -*- coding: utf-8 -*-
import numpy as np


class RationStatistics:
    # модуль для проведения статистического анализа рационов за период

    def __init__(self, rations_data):
        """
        rations_data: список словарей с итогами за день
        [{'date': ..., 'calories': ..., 'protein': ..., ...}, ...]
        """
        self.data = rations_data

    def get_average_calories(self):
        # расчет среднего потребления калорий
        if not self.data:
            return 0
        calories = [r["calories"] for r in self.data]
        return np.mean(calories)

    def get_std_deviation(self):
        # расчет стандартного отклонения калорийности - стабильность питания
        if not self.data:
            return 0
        calories = [r["calories"] for r in self.data]
        return np.std(calories)

    def find_trends(self):
        # анализ тренда калорийности - рост/падение/плато
        if len(self.data) < 3:
            return "Недостаточно данных для анализа тренда"

        calories = [r["calories"] for r in self.data]
        x = np.arange(len(calories))
        # линейная регрессия
        slope, intercept = np.polyfit(x, calories, 1)

        if slope > 50:
            return "Тренд увеличения калорийности"
        if slope < -50:
            return "Тренд снижения калорийности"
        return "Стабильное потребление (плато)"

    def get_summary_report(self):
        # формирование сводного отчета (статистика)
        return {
            "avg_kcal": round(self.get_average_calories(), 1),
            "stability": round(self.get_std_deviation(), 1),
            "trend": self.find_trends(),
        }
