# -*- coding: utf-8 -*-
from app.models import User, Product, AuditLog
from app import db


class AdminService:

    @staticmethod
    def get_system_overview():
        return {
            "total_users": User.query.count(),
            "total_products": Product.query.count(),
            "recent_logs": AuditLog.query.order_by(AuditLog.timestamp.desc())
            .limit(10)
            .all(),
        }

    @staticmethod
    def toggle_user_role(user_id):
        user = User.query.get(user_id)
        if not user:
            return False

        user.role = "admin" if user.role == "operator" else "operator"
        db.session.commit()
        return True

    @staticmethod
    def cleanup_old_logs(days=30):
        import datetime

        threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        deleted = AuditLog.query.filter(AuditLog.timestamp < threshold).delete()
        db.session.commit()
        return deleted
