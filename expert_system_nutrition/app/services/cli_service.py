# -*- coding: utf-8 -*-
import click
from app import db
from app.models import User, Product


class CLIService:

    @staticmethod
    def create_admin_interactive():
        username = click.prompt("Введите логин нового администратора", type=str)
        password = click.prompt(
            "Введите пароль", hide_input=True, confirmation_prompt=True
        )

        if User.query.filter_by(username=username).first():
            return

        user = User(username=username, role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Администратор {username} успешно создан.")

    @staticmethod
    def list_all_routes(app):
        import urllib

        output = []
        for rule in app.url_map.iter_rules():
            options = {}
            for arg in rule.arguments:
                options[arg] = f"[{arg}]"

            methods = ",".join(rule.methods)
            url = urllib.parse.unquote(str(rule))
            line = f"{rule.endpoint:50s} {methods:20s} {url}"
            output.append(line)

        for line in sorted(output):
            click.echo(line)

    @staticmethod
    def export_products_to_json(filename="products_export.json"):
        import json

        products = Product.query.all()
        data = [
            {
                "id": p.id,
                "name": p.name,
                "kcal": p.calories_per_100g,
                "p": p.proteins_per_100g,
                "f": p.fats_per_100g,
                "c": p.carbs_per_100g,
            }
            for p in products
        ]

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        click.echo(f"Экспортировано {len(data)} продуктов в {filename}")
