# -*- coding: utf-8 -*-
from app.models import UserProfile, User


def test_profile_norms_male(app):
    with app.app_context():
        p = UserProfile(
            gender="male", weight=80, height=180, age=30, activity_level=1.2
        )
        p.calculate_daily_norms()
        assert round(p.target_calories) == 2136
        assert p.target_protein > 0


def test_profile_norms_female(app):
    with app.app_context():
        p = UserProfile(
            gender="female", weight=60, height=165, age=25, activity_level=1.375
        )
        p.calculate_daily_norms()
        # BMR = 10*60 + 6.25*165 - 5*25 - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
        # TDEE = 1345.25 * 1.375 = 1849.7
        assert 1840 < p.target_calories < 1860


def test_audit_logging(client, auth_user):
    client.post("/api/login", json={"username": "testuser", "password": "testpass"})

    client.post(
        "/api/profile", json={"age": 20, "weight": 70, "height": 175, "gender": "male"}
    )

    from app.models import AuditLog

    with client.application.app_context():
        logs = AuditLog.query.filter_by(user_id=auth_user.id).all()
        assert len(logs) > 0
        assert "профил" in logs[0].action.lower()
