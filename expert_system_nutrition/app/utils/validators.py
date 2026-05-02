# -*- coding: utf-8 -*-
import re


class DataValidator:
    # модуль валидации входящих данных приложения

    @staticmethod
    def validate_username(username):
        # валидация логина
        if not username or len(username) < 3 or len(username) > 64:
            return False, "Логин должен быть от 3 до 64 символов"
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            return (
                False,
                "Логин может содержать только латинские буквы, цифры и подчеркивание",
            )
        return True, ""

    @staticmethod
    def validate_password(password):
        # валидация пароля
        if not password or len(password) < 6:
            return False, "Пароль должен быть не менее 6 символов"
        return True, ""

    @staticmethod
    def validate_product_data(data):
        # валидация данных продукта
        required = ["name", "calories", "proteins", "fats", "carbs"]
        for field in required:
            if field not in data:
                return False, f"Отсутствует обязательное поле: {field}"

        if len(data["name"]) < 2:
            return False, "Название продукта слишком короткое"

        try:
            for field in ["calories", "proteins", "fats", "carbs"]:
                val = float(data[field])
                if val < 0 or val > 1000:
                    return False, f"Некорректное значение для {field}"
        except ValueError:
            return False, "Питательные вещества должны быть числовыми"

        return True, ""

    @staticmethod
    def validate_date(date_str):
        # валидация формата даты
        try:
            import datetime

            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
