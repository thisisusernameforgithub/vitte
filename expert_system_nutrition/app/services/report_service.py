# -*- coding: utf-8 -*-
import csv
import io
from app.models import Ration


class ReportService:

    @staticmethod
    def generate_csv_ration_report(ration_id):
        ration = Ration.query.get(ration_id)
        if not ration:
            return None

        si = io.StringIO()
        cw = csv.writer(si, delimiter=";")

        # Заголовки
        cw.writerow(["Дата", ration.date.isoformat()])
        cw.writerow(["Пользователь ID", ration.user_id])
        cw.writerow([])
        cw.writerow(["Продукт", "Вес (г)", "Ккал", "Белки", "Жиры", "Углеводы"])

        totals = {"c": 0, "p": 0, "f": 0, "cb": 0}
        for item in ration.items:
            f = item.weight / 100
            c = item.product.calories_per_100g * f
            p = item.product.proteins_per_100g * f
            fat = item.product.fats_per_100g * f
            cb = item.product.carbs_per_100g * f

            cw.writerow(
                [
                    item.product.name,
                    item.weight,
                    round(c, 1),
                    round(p, 1),
                    round(fat, 1),
                    round(cb, 1),
                ]
            )
            totals["c"] += c
            totals["p"] += p
            totals["f"] += fat
            totals["cb"] += cb

        cw.writerow([])
        cw.writerow(
            [
                "ИТОГО",
                "",
                round(totals["c"], 1),
                round(totals["p"], 1),
                round(totals["f"], 1),
                round(totals["cb"], 1),
            ]
        )

        return si.getvalue()

    @staticmethod
    def generate_system_summary_csv():
        from app.models import User, Ration

        si = io.StringIO()
        cw = csv.writer(si, delimiter=";")
        cw.writerow(["User ID", "Username", "Rations Count", "Total Calories Sum"])

        users = User.query.all()
        for u in users:
            rations = u.rations.all()
            total_cal = 0
            for r in rations:
                for item in r.items:
                    total_cal += item.product.calories_per_100g * item.weight / 100
            cw.writerow([u.id, u.username, len(rations), round(total_cal, 1)])

        return si.getvalue()
