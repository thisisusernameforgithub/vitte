# -*- coding: utf-8 -*-

# Модели БД

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


from datetime import datetime


# модель User для таблицы users, которая хранит информацию о пользователях
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(
        db.Integer, primary_key=True, comment="Уникальный идентификатор пользователя"
    )
    username = db.Column(
        db.String(64),
        index=True,
        unique=True,
        nullable=False,
        comment="Имя пользователя для входа",
    )
    password_hash = db.Column(
        db.String(256), nullable=False, comment="Хеш пароля пользователя"
    )

    # роль пользователя
    role = db.Column(
        db.String(20),
        nullable=False,
        default="operator",
        comment="Роль пользователя в системе (admin, operator)",
    )

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, comment="Дата регистрации"
    )

    rations = db.relationship("Ration", backref="user", lazy="dynamic")
    profile = db.relationship(
        "UserProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    logs = db.relationship("AuditLog", backref="user", lazy="dynamic")
    feedbacks = db.relationship("Feedback", backref="user", lazy="dynamic")

    def set_password(self, password):
        # установка пароля с использованием хеширования
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # чексумма
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        # проверка является ли пользователь администратором
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username}>"


class UserProfile(db.Model):
    # профиль пользователя с физиологическими данными.
    __tablename__ = "user_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    age = db.Column(db.Integer, comment="Возраст пользователя")
    weight = db.Column(db.Float, comment="Вес в килограммах")
    height = db.Column(db.Float, comment="Рост в сантиметрах")
    gender = db.Column(db.String(10), comment="Пол (male/female)")
    activity_level = db.Column(
        db.Float, default=1.2, comment="Коэффициент физической активности"
    )

    # Расчетные цели
    target_calories = db.Column(db.Float, comment="Целевая калорийность")
    target_protein = db.Column(db.Float, comment="Целевой белок")
    target_fat = db.Column(db.Float, comment="Целевые жиры")
    target_carbs = db.Column(db.Float, comment="Целевые углеводы")

    def calculate_daily_norms(self):

        # мат. расчет норм по формуле Миффлина-Сан Жеора.

        if not all([self.weight, self.height, self.age, self.gender]):
            return False

        # базовый метаболизм (BMR)
        if self.gender == "male":
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

        # учет активности
        self.target_calories = bmr * self.activity_level

        # рекомендуемое распределение БЖУ (белки - 20%, жиры - 30%, углеводы - 50%)
        self.target_protein = (self.target_calories * 0.20) / 4
        self.target_fat = (self.target_calories * 0.30) / 9
        self.target_carbs = (self.target_calories * 0.50) / 4
        return True


class AuditLog(db.Model):
    # аудит действий операторов

    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(256), nullable=False, comment="Описание действия")
    ip_address = db.Column(db.String(45), comment="IP адрес инициатора")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Article(db.Model):
    # будущая база знаний

    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, comment="Заголовок статьи")
    content = db.Column(db.Text, nullable=False, comment="Текст статьи")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Article {self.title}>"


class HealthGoal(db.Model):
    # цели пользователя по изменению веса и здоровья

    __tablename__ = "health_goals"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    goal_type = db.Column(
        db.String(50), nullable=False
    )  # 'weight_loss', 'muscle_gain', 'maintenance'
    target_weight = db.Column(db.Float)
    deadline = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)

    def get_progress(self, current_weight):
        if not self.target_weight:
            return 0
        diff = abs(current_weight - self.target_weight)
        return max(0, 100 - diff)


class Feedback(db.Model):
    # фидбек
    __tablename__ = "feedbacks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    ration_id = db.Column(db.Integer, db.ForeignKey("rations.id"))
    rating = db.Column(db.Integer, comment="Оценка точности системы (1-5)")
    comment = db.Column(db.Text, comment="Комментарий пользователя")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# модель Product для таблицы products, которая хранит информацию о продуктах и пищевой ценности
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(
        db.Integer, primary_key=True, comment="Уникальный идентификатор продукта"
    )
    name = db.Column(
        db.String(128),
        index=True,
        unique=True,
        nullable=False,
        comment="Название продукта",
    )
    calories_per_100g = db.Column(
        db.Float, nullable=False, comment="Калории на 100 г продукта"
    )
    proteins_per_100g = db.Column(
        db.Float, nullable=False, comment="Белки (г) на 100 г продукта"
    )
    fats_per_100g = db.Column(
        db.Float, nullable=False, comment="Жиры (г) на 100 г продукта"
    )
    carbs_per_100g = db.Column(
        db.Float, nullable=False, comment="Углеводы (г) на 100 г продукта"
    )

    def __repr__(self):
        return f"<Product {self.name}>"


# модель Ration для таблицы rations - суточный рацион конкретного пользователя
class Ration(db.Model):
    __tablename__ = "rations"
    id = db.Column(
        db.Integer, primary_key=True, comment="Уникальный идентификатор рациона"
    )
    date = db.Column(
        db.Date, nullable=False, index=True, comment="Дата, за которую составлен рацион"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        comment="Идентификатор пользователя к которому относится рацион",
    )

    items = db.relationship(
        "RationItem", backref="ration", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Ration id={self.id} user_id={self.user_id} date={self.date}>"


# модель RationItem для таблицы ration_items - один продукт в рамках конкретного суточного рациона
class RationItem(db.Model):
    __tablename__ = "ration_items"
    id = db.Column(
        db.Integer,
        primary_key=True,
        comment="Уникальный идентификатор элемента рациона",
    )
    # вес
    weight = db.Column(
        db.Float,
        nullable=False,
        comment="Вес продукта в данном приеме пищи (в граммах)",
    )

    ration_id = db.Column(
        db.Integer,
        db.ForeignKey("rations.id"),
        nullable=False,
        comment="Идентификатор рациона, к которому относится элемент",
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False,
        comment="Идентификатор продукта в этом элементе",
    )

    product = db.relationship("Product")

    def __repr__(self):
        return f"<RationItem id={self.id} product_id={self.product_id} weight={self.weight}>"
