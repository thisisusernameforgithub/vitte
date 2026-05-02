# -*- coding: utf-8 -*-
import math


class NutrientConverter:
    # модуль преобразования единиц измерения нутриентов

    @staticmethod
    def grams_to_kcal(protein=0, fat=0, carbs=0):
        # конвертация грамм БЖУ в ккал
        return (protein * 4) + (fat * 9) + (carbs * 4)

    @staticmethod
    def get_percentage_distribution(protein_kcal, fat_kcal, carbs_kcal):
        # расчет процентного распределения энергии по нутриентам
        total = protein_kcal + fat_kcal + carbs_kcal
        if total == 0:
            return 0, 0, 0
        return (
            (protein_kcal / total) * 100,
            (fat_kcal / total) * 100,
            (carbs_kcal / total) * 100,
        )

    @staticmethod
    def calculate_bmi(weight_kg, height_cm):
        # пасчет индекса массы тела
        if height_cm <= 0:
            return 0
        height_m = height_cm / 100
        return weight_kg / (height_m**2)

    @staticmethod
    def interpret_bmi(bmi):
        # интерпретация ИМТ согласно классификации ВОЗ
        if bmi < 16:
            return "Выраженный дефицит массы тела"
        if 16 <= bmi < 18.5:
            return "Недостаточная масса тела"
        if 18.5 <= bmi < 25:
            return "Норма"
        if 25 <= bmi < 30:
            return "Избыточная масса тела (предожирение)"
        if 30 <= bmi < 35:
            return "Ожирение I степени"
        if 35 <= bmi < 40:
            return "Ожирение II степени"
        return "Ожирение III степени"
