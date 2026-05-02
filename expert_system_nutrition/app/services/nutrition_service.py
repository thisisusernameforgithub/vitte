# -*- coding: utf-8 -*-
from app.models import Ration, RationItem, UserProfile
from app import db
import datetime


class NutritionService:

    @staticmethod
    def get_or_create_ration(user_id, date_obj):
        ration = Ration.query.filter_by(user_id=user_id, date=date_obj).first()
        if not ration:
            ration = Ration(user_id=user_id, date=date_obj)
            db.session.add(ration)
            db.session.commit()
        return ration

    @staticmethod
    def add_item_to_ration(user_id, product_id, weight, date_str):
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        ration = NutritionService.get_or_create_ration(user_id, date_obj)

        item = RationItem(
            ration_id=ration.id, product_id=product_id, weight=float(weight)
        )
        db.session.add(item)
        db.session.commit()
        return ration

    @staticmethod
    def calculate_totals(ration):
        totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        for item in ration.items:
            weight_factor = item.weight / 100
            totals["calories"] += item.product.calories_per_100g * weight_factor
            totals["protein"] += item.product.proteins_per_100g * weight_factor
            totals["fat"] += item.product.fats_per_100g * weight_factor
            totals["carbs"] += item.product.carbs_per_100g * weight_factor
        return {k: round(v, 1) for k, v in totals.items()}

    @staticmethod
    def generate_health_tips(user_id):
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        tips = []
        if not profile:
            return ["Заполните профиль для получения персональных советов."]

        if profile.weight and profile.height:
            bmi = profile.weight / ((profile.height / 100) ** 2)
            if bmi > 25:
                tips.append("Рекомендуется снизить потребление быстрых углеводов.")
            elif bmi < 18.5:
                tips.append("Обратите внимание на высокобелковые продукты.")

        return (
            tips
            if tips
            else ["Ваш рацион и показатели в норме. Продолжайте в том же духе!"]
        )
