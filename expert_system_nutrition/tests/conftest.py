# -*- coding: utf-8 -*-
import pytest
from app import create_app, db
from app.models import User, Product, UserProfile
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # Seed basic data
        p1 = Product(
            name="Apple",
            calories_per_100g=52,
            proteins_per_100g=0.3,
            fats_per_100g=0.2,
            carbs_per_100g=14,
        )
        db.session.add(p1)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_user(app):
    with app.app_context():
        u = User(username="testuser")
        u.set_password("testpass")
        db.session.add(u)
        db.session.commit()
        return u
