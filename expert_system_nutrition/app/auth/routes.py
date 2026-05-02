# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User, AuditLog
from app.auth import auth_bp

from app.utils.validators import DataValidator
from app.utils.decorators import log_action


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            msg = "Неверный логин или пароль"
            return jsonify({"status": "error", "message": msg}), (
                401 if request.is_json else render_template("login.html", error=msg)
            )

        login_user(user, remember=True)

        log = AuditLog(
            user_id=user.id, action="Вход в систему", ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()

        return (
            jsonify({"status": "success"})
            if request.is_json
            else redirect(url_for("main.index"))
        )

    return render_template("login.html", title="Вход")


@auth_bp.route("/logout")
@log_action("Выход из системы")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        data = request.get_json() if request.is_json else request.form
        username = data.get("username")
        password = data.get("password")

        # Валидация
        is_valid, error_msg = DataValidator.validate_username(username)
        if not is_valid:
            return jsonify({"status": "error", "message": error_msg}), 400

        is_valid, error_msg = DataValidator.validate_password(password)
        if not is_valid:
            return jsonify({"status": "error", "message": error_msg}), 400

        if User.query.filter_by(username=username).first():
            return (
                jsonify({"status": "error", "message": "Имя пользователя уже занято"}),
                400,
            )

        user = User(username=username, role="operator")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        log = AuditLog(
            user_id=user.id,
            action="Регистрация нового пользователя",
            ip_address=request.remote_addr,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({"status": "success", "message": "Регистрация успешна"})

    return render_template("register.html", title="Регистрация")
