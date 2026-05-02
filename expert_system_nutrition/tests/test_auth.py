# -*- coding: utf-8 -*-
import pytest
from app.models import User


def test_password_hashing(app):
    with app.app_context():
        u = User(username="susan")
        u.set_password("cat")
        assert not u.check_password("dog")
        assert u.check_password("cat")


def test_registration(client, app):
    # Test successful registration
    response = client.post(
        "/api/register", json={"username": "newuser", "password": "password123"}
    )
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(username="newuser").first() is not None


def test_login_logout(client, auth_user):
    # Success login
    response = client.post(
        "/api/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200

    # Logout
    response = client.get("/api/logout")
    assert response.status_code == 200
