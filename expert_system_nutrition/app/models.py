# -*- coding: utf-8 -*-

# Модели БД

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


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
        default="patient",
        comment="Роль пользователя в системе",
    )

    rations = db.relationship("Ration", backref="user", lazy="dynamic")

    def set_password(self, password):
        # установка пароля
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # чексумма
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


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
