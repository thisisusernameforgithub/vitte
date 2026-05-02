# -*- coding: utf-8 -*-
from app.services.nutrition_service import NutritionService
from app.services.admin_service import AdminService
from app.models import Product


def test_nutrition_service_calculation(app):
    with app.app_context():
        p = Product.query.first()
        from app.models import Ration, RationItem

        r = Ration(user_id=1, date=datetime.date.today())
        db.session.add(r)
        db.session.commit()
        item = RationItem(ration_id=r.id, product_id=p.id, weight=100)
        db.session.add(item)
        db.session.commit()

        totals = NutritionService.calculate_totals(r)
        assert totals["calories"] == p.calories_per_100g


def test_admin_service_overview(app):
    with app.app_context():
        overview = AdminService.get_system_overview()
        assert "total_users" in overview
        assert "total_products" in overview


def test_health_tips_logic(app, auth_user):
    with app.app_context():
        tips = NutritionService.generate_health_tips(auth_user.id)
        assert len(tips) > 0
        assert isinstance(tips[0], str)
