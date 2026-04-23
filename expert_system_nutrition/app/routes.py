# -*- coding: utf-8 -*-

# Маршруты

from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Product, Ration, RationItem
import datetime

from app.ml_model import RationEvaluator

main_bp = Blueprint("main", __name__)
ration_evaluator = RationEvaluator()


# фронт
@main_bp.route("/")
@login_required
def index():
    return render_template("index.html", title="Главная")


@main_bp.route("/login")
def login_page():
    return render_template("login.html", title="Вход")


@main_bp.route("/register")
def register_page():
    return render_template("register.html", title="Регистрация")


# бек
@main_bp.route("/api/register", methods=["POST"])
def register():
    # API регистрации
    data = request.get_json() or {}
    if "username" not in data or "password" not in data:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Отсутствует имя пользователя или пароль",
                }
            ),
            400,
        )
    if User.query.filter_by(username=data["username"]).first():
        return (
            jsonify({"status": "error", "message": "Это имя пользователя занято"}),
            400,
        )

    user = User(username=data["username"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"status": "success", "message": "Пользователь зарегистрирован"})


@main_bp.route("/api/login", methods=["POST"])
def login():
    # API аутентификации
    data = request.get_json() or {}
    user = User.query.filter_by(username=data.get("username")).first()
    if user is None or not user.check_password(data.get("password")):
        return (
            jsonify(
                {"status": "error", "message": "Неверное имя пользователя или пароль"}
            ),
            401,
        )

    login_user(user, remember=True)
    return jsonify({"status": "success"})


@main_bp.route("/api/logout")
@login_required
def logout():
    # API выхода
    logout_user()
    return jsonify({"status": "success"})


@main_bp.route("/api/products")
@login_required
def get_products():
    # API поиска
    query = request.args.get("q", "")
    if len(query) < 2:
        return jsonify([])

    products = Product.query.filter(Product.name.ilike(f"%{query}%")).limit(10).all()
    return jsonify([{"id": p.id, "name": p.name} for p in products])


@main_bp.route("/api/rations/items", methods=["POST"])
@login_required
def add_ration_item():
    # API добавления
    data = request.get_json() or {}
    product_id = data.get("product_id")
    weight = data.get("weight")
    date_str = data.get("date", datetime.date.today().isoformat())

    if not product_id or not weight:
        return (
            jsonify({"status": "error", "message": "Отсутствует ID продукта или вес"}),
            400,
        )

    ration_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    ration = Ration.query.filter_by(user_id=current_user.id, date=ration_date).first()
    if not ration:
        ration = Ration(user_id=current_user.id, date=ration_date)
        db.session.add(ration)
        db.session.commit()

    item = RationItem(ration_id=ration.id, product_id=product_id, weight=int(weight))
    db.session.add(item)
    db.session.commit()

    current_app.logger.info(
        f"DB: Успешно добавлен продукт id={product_id} в рацион {ration.id} для пользователя {current_user.id}"
    )

    return get_ration_by_date(date_str)


@main_bp.route("/api/rations/items/<int:item_id>", methods=["DELETE"])
@login_required
def delete_ration_item(item_id):
    # API удаления
    item = RationItem.query.get_or_404(item_id)

    if item.ration.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Доступ запрещен"}), 403

    date_str = item.ration.date.isoformat()
    db.session.delete(item)
    db.session.commit()

    current_app.logger.info(
        f"DB: Успешно удален продукт id={item_id} из рациона {item.ration.id}"
    )

    return get_ration_by_date(date_str)


@main_bp.route("/api/rations/<string:date_str>")
@login_required
def get_ration_by_date(date_str):
    # API рациона
    db.session.expire_all()

    current_app.logger.info(
        f"API: Пользователь {current_user.id} запрашивает рацион за {date_str}."
    )

    ration_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    ration = Ration.query.filter_by(user_id=current_user.id, date=ration_date).first()

    if not ration:
        current_app.logger.warning(
            f"API: Рацион для пользователя {current_user.id} на {date_str} не найден в БД."
        )
        return jsonify(
            {
                "items": [],
                "totals": {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0},
            }
        )

    db_items = db.session.query(RationItem).filter_by(ration_id=ration.id).all()
    current_app.logger.info(
        f"DB: Найдено {len(db_items)} продуктов в рационе {ration.id}."
    )

    items_data = []
    totals = {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0}
    for item in db_items:
        calories = (item.product.calories_per_100g / 100) * item.weight
        proteins = (item.product.proteins_per_100g / 100) * item.weight
        fats = (item.product.fats_per_100g / 100) * item.weight
        carbs = (item.product.carbs_per_100g / 100) * item.weight

        items_data.append(
            {
                "id": item.id,
                "name": item.product.name,
                "weight": item.weight,
                "calories": round(calories),
                "proteins": round(proteins, 1),
                "fats": round(fats, 1),
                "carbs": round(carbs, 1),
            }
        )
        totals["calories"] += calories
        totals["proteins"] += proteins
        totals["fats"] += fats
        totals["carbs"] += carbs

    for key in totals:
        totals[key] = round(totals[key], 1)

    current_app.logger.info(f"API: Отправка JSON с {len(items_data)} продуктами.")
    return jsonify({"items": items_data, "totals": totals})


@main_bp.route("/api/rations/evaluate", methods=["POST"])
@login_required
def evaluate_ration():
    # API оценки
    data = request.get_json() or {}
    date_str = data.get("date", datetime.date.today().isoformat())
    ration_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    ration = Ration.query.filter_by(user_id=current_user.id, date=ration_date).first()
    if not ration or not ration.items.first():
        return jsonify({"status": "error", "message": "Рацион на эту дату пуст"}), 404

    totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
    for item in ration.items:
        totals["calories"] += (item.product.calories_per_100g / 100) * item.weight
        totals["protein"] += (item.product.proteins_per_100g / 100) * item.weight
        totals["fat"] += (item.product.fats_per_100g / 100) * item.weight
        totals["carbs"] += (item.product.carbs_per_100g / 100) * item.weight

    # 1. получаем основное предсказание от модели
    base_prediction = ration_evaluator.predict(totals)

    # 2. добавляет детали на основе простых правил (для стандарта в 2000 кккал)
    details = []
    # нормы БЖУ (условные)
    IDEAL_PROTEIN = 100
    IDEAL_FAT = 70
    IDEAL_CARBS = 245

    if totals["protein"] < IDEAL_PROTEIN * 0.8:
        details.append("отмечается недостаток белка")

    if totals["fat"] > IDEAL_FAT * 1.2:
        details.append("повышенное потребление жиров")

    if totals["carbs"] < IDEAL_CARBS * 0.8:
        details.append("недостаточное потребление углеводов")

    # 3. генерация финального сообщения
    if details:
        final_evaluation = f"{base_prediction}. При этом, {', '.join(details)}"
    else:
        final_evaluation = f"{base_prediction}. Основные макронутриенты в норме"

    return jsonify({"status": "success", "evaluation": final_evaluation})


# дебаг (без аутентификации)
# @main_bp.route("/debug/product-check")
# def debug_product_check():
#     try:
#         product_count = Product.query.count()
#         if product_count > 0:
#             sample_products = Product.query.limit(5).all()
#             sample_names = [p.name for p in sample_products]
#             return jsonify(
#                 {
#                     "status": "success",
#                     "product_count": product_count,
#                     "samples": sample_names,
#                 }
#             )
#         else:
#             return jsonify(
#                 {
#                     "status": "empty",
#                     "product_count": 0,
#                     "message": "Таблица продуктов пуста.",
#                 }
#             )
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500
