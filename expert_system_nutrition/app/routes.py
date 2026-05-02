# -*- coding: utf-8 -*-

# Маршруты

from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import (
    User,
    Product,
    Ration,
    RationItem,
    UserProfile,
    AuditLog,
    Article,
    HealthGoal,
)
import datetime
import io
import csv

from app.ml_model import RationEvaluator
from app.utils.converters import NutrientConverter
from app.utils.statistics import RationStatistics
from app.utils.decorators import admin_required, log_action
from app.services.nutrition_service import NutritionService

main_bp = Blueprint("main", __name__)
ration_evaluator = RationEvaluator()


# фронт
@main_bp.route("/")
@login_required
def index():
    return render_template("index.html", title="Панель оператора")


# API
@main_bp.route("/api/profile", methods=["GET", "POST"])
@login_required
def profile_api():
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)

    if request.method == "POST":
        data = request.get_json() or {}
        profile.age = data.get("age", profile.age)
        profile.weight = data.get("weight", profile.weight)
        profile.height = data.get("height", profile.height)
        profile.gender = data.get("gender", profile.gender)
        profile.activity_level = data.get("activity_level", profile.activity_level)

        profile.calculate_daily_norms()
        db.session.commit()

        return jsonify({"status": "success", "message": "Данные профиля обновлены"})

    return jsonify(
        {
            "age": profile.age,
            "weight": profile.weight,
            "height": profile.height,
            "gender": profile.gender,
            "activity_level": profile.activity_level,
            "norms": {
                "calories": profile.target_calories,
                "protein": profile.target_protein,
                "fat": profile.target_fat,
                "carbs": profile.target_carbs,
            },
        }
    )


@main_bp.route("/api/dashboard")
@login_required
def dashboard_api():
    # аналитика
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()

    # расчет ИМТ
    bmi_data = None
    if profile and profile.weight and profile.height:
        bmi = NutrientConverter.calculate_bmi(profile.weight, profile.height)
        bmi_data = {
            "value": round(bmi, 1),
            "interpretation": NutrientConverter.interpret_bmi(bmi),
        }

    # сбор статистики за последнию неделю
    seven_days_ago = datetime.date.today() - datetime.timedelta(days=7)
    recent_rations = Ration.query.filter(
        Ration.user_id == current_user.id, Ration.date >= seven_days_ago
    ).all()

    rations_list = []
    for r in recent_rations:
        day_totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        for item in r.items:
            day_totals["calories"] += (
                item.product.calories_per_100g / 100
            ) * item.weight
            day_totals["protein"] += (
                item.product.proteins_per_100g / 100
            ) * item.weight
            day_totals["fat"] += (item.product.fats_per_100g / 100) * item.weight
            day_totals["carbs"] += (item.product.carbs_per_100g / 100) * item.weight
        rations_list.append(day_totals)

    stats_calculator = RationStatistics(rations_list)
    stats_report = stats_calculator.get_summary_report()

    return jsonify(
        {"bmi": bmi_data, "statistics": stats_report, "days_tracked": len(rations_list)}
    )


@main_bp.route("/api/admin/products", methods=["GET", "POST"])
@login_required
@admin_required
def admin_products_api():
    # управление каталогом продуктов
    if request.method == "POST":
        data = request.get_json() or {}
        product = Product(
            name=data.get("name"),
            calories_per_100g=float(data.get("calories")),
            proteins_per_100g=float(data.get("proteins", 0)),
            fats_per_100g=float(data.get("fats", 0)),
            carbs_per_100g=float(data.get("carbs", 0)),
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({"status": "success", "id": product.id})

    products = Product.query.limit(50).all()
    return jsonify(
        [
            {"id": p.id, "name": p.name, "calories": p.calories_per_100g}
            for p in products
        ]
    )


@main_bp.route("/api/admin/users")
@login_required
@admin_required
def admin_users_api():
    # пользователи системы
    users = User.query.all()
    return jsonify(
        [{"id": u.id, "username": u.username, "role": u.role} for u in users]
    )


@main_bp.route("/api/products")
@login_required
def get_products():
    # поиск продуктов
    query = request.args.get("q", "")
    if len(query) < 2:
        return jsonify([])

    products = Product.query.filter(Product.name.ilike(f"%{query}%")).limit(15).all()
    return jsonify([{"id": p.id, "name": p.name} for p in products])


@main_bp.route("/api/rations/items", methods=["POST"])
@login_required
def add_ration_item():
    # API добавление продукта
    data = request.get_json() or {}
    product_id = data.get("product_id")
    weight = data.get("weight")
    date_str = data.get("date", datetime.date.today().isoformat())

    if not product_id or not weight:
        return jsonify({"status": "error", "message": "Данные не полны"}), 400

    NutritionService.add_item_to_ration(current_user.id, product_id, weight, date_str)

    return get_ration_by_date(date_str)


@main_bp.route("/api/rations/items/<int:item_id>", methods=["DELETE"])
@login_required
def delete_ration_item(item_id):
    # удаление продукта
    item = RationItem.query.get_or_404(item_id)
    if item.ration.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Доступ запрещен"}), 403

    date_str = item.ration.date.isoformat()
    db.session.delete(item)
    db.session.commit()

    return get_ration_by_date(date_str)


@main_bp.route("/api/rations/<string:date_str>")
@login_required
def get_ration_by_date(date_str):
    # получение состава рациона
    db.session.expire_all()
    ration_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    ration = Ration.query.filter_by(user_id=current_user.id, date=ration_date).first()

    if not ration:
        return jsonify(
            {
                "items": [],
                "totals": {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0},
            }
        )

    items_data = []
    totals = {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0}
    for item in ration.items:
        c = (item.product.calories_per_100g / 100) * item.weight
        p = (item.product.proteins_per_100g / 100) * item.weight
        f = (item.product.fats_per_100g / 100) * item.weight
        cb = (item.product.carbs_per_100g / 100) * item.weight

        items_data.append(
            {
                "id": item.id,
                "name": item.product.name,
                "weight": item.weight,
                "calories": round(c),
                "proteins": round(p, 1),
                "fats": round(f, 1),
                "carbs": round(cb, 1),
            }
        )
        totals["calories"] += c
        totals["proteins"] += p
        totals["fats"] += f
        totals["carbs"] += cb

    for key in totals:
        totals[key] = round(totals[key], 1)
    return jsonify({"items": items_data, "totals": totals})


@main_bp.route("/api/rations/evaluate", methods=["POST"])
@login_required
@log_action("Интеллектуальная оценка рациона")
def evaluate_ration():
    # интеллектуальная оценка рациона
    data = request.get_json() or {}
    date_str = data.get("date", datetime.date.today().isoformat())
    ration_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    ration = Ration.query.filter_by(user_id=current_user.id, date=ration_date).first()
    if not ration or not ration.items.first():
        return jsonify({"status": "error", "message": "Рацион пуст"}), 404

    # расчет итогов
    totals = NutritionService.calculate_totals(ration)

    base_prediction = ration_evaluator.predict(totals)
    profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    details = []

    if profile and profile.target_calories:
        diff = (totals["calories"] / profile.target_calories) * 100
        if diff < 85:
            details.append(f"дефицит энергии ({round(100-diff)}%)")
        elif diff > 115:
            details.append(f"избыток энергии ({round(diff-100)}%)")

    final_evaluation = f"{base_prediction}. " + (
        f"Замечено: {', '.join(details)}." if details else "Показатели в норме"
    )
    return jsonify({"status": "success", "evaluation": final_evaluation})


@main_bp.route("/api/articles", methods=["GET", "POST"])
@login_required
def articles_api():
    # управление wiki
    if request.method == "POST":
        if not current_user.is_admin():
            return jsonify({"status": "error"}), 403
        data = request.get_json() or {}
        article = Article(
            title=data.get("title"),
            content=data.get("content"),
            author_id=current_user.id,
        )
        db.session.add(article)
        db.session.commit()
        return jsonify({"status": "success", "id": article.id})

    articles = Article.query.all()
    return jsonify([{"id": a.id, "title": a.title} for a in articles])


@main_bp.route("/api/export/csv/<string:date_str>")
@login_required
def export_csv(date_str):
    # экспорт рациона в csv
    ration_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    ration = Ration.query.filter_by(user_id=current_user.id, date=ration_date).first()
    if not ration:
        return jsonify({"status": "error"}), 404

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Продукт", "Вес (г)", "Ккал", "Белки", "Жиры", "Углеводы"])
    for item in ration.items:
        wf = item.weight / 100
        writer.writerow(
            [
                item.product.name,
                item.weight,
                round(item.product.calories_per_100g * wf, 1),
                round(item.product.proteins_per_100g * wf, 1),
                round(item.product.fats_per_100g * wf, 1),
                round(item.product.carbs_per_100g * wf, 1),
            ]
        )

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"ration_{date_str}.csv",
    )
