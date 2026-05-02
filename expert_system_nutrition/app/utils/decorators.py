# -*- coding: utf-8 -*-
import re
from functools import wraps
from flask import request, jsonify
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            return (
                jsonify(
                    {"status": "error", "message": "Требуются права администратора"}
                ),
                403,
            )
        return f(*args, **kwargs)

    return decorated_function


def log_action(action_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app import db
            from app.models import AuditLog

            response = f(*args, **kwargs)

            if hasattr(response, "status_code") and response.status_code == 200:
                log = AuditLog(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    action=action_name,
                    ip_address=request.remote_addr,
                )
                db.session.add(log)
                db.session.commit()
            return response

        return decorated_function

    return decorator
