# -*- coding: utf-8 -*-

# Cкрипт для запуска приложения

import os
import pandas as pd
import click
import datetime
from app import create_app, db
from app.models import User, Product, UserProfile, Ration, RationItem

# cоздаем экземпляр приложения
app = create_app()


@app.cli.command("load-data")
def load_data_command():
    # загрузка справочника
    import csv

    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "ABBREV_with_CLASS.csv"
    )

    if not os.path.exists(csv_path):
        click.echo(f"Ошибка: файл {csv_path} не найден")
        return

    click.echo("Загрузка из справочника ...")

    try:
        db.session.query(Product).delete()

        products_to_add = []
        processed_names = set()
        skipped_rows = 0

        with open(csv_path, mode="r", encoding="utf-8") as infile:
            reader = csv.reader(infile, delimiter=";")
            next(reader, None)

            # очистка справочника
            for row in reader:
                try:
                    if len(row) < 9:
                        skipped_rows += 1
                        continue

                    name = row[2].strip()

                    if not name or name in processed_names:
                        skipped_rows += 1
                        continue

                    calories = float(row[4].replace(",", "."))
                    proteins = float(row[5].replace(",", "."))
                    fats = float(row[6].replace(",", "."))
                    carbs = float(row[8].replace(",", "."))

                    product = Product(
                        name=name,
                        calories_per_100g=calories,
                        proteins_per_100g=proteins,
                        fats_per_100g=fats,
                        carbs_per_100g=carbs,
                    )
                    products_to_add.append(product)
                    processed_names.add(name)

                except (ValueError, IndexError):
                    skipped_rows += 1
                    continue

        db.session.bulk_save_objects(products_to_add)
        db.session.commit()

        click.echo(f"Успешно загружено {len(products_to_add)} уникальных продуктов")
        if skipped_rows > 0:
            click.echo(
                f"Пропущено {skipped_rows} строк из-за ошибок/дубликатов/пустых полей"
            )

    except Exception as e:
        db.session.rollback()
        click.echo(f"Ошибка во время загрузки: {e}")


@app.cli.command("reset-db")
def reset_db_command():
    # ресет БД (удаляет файл БД)
    if click.confirm("Вы уверены что хотите удалить файл БД?", abort=True):
        db.session.remove()

        db_path = os.path.join(os.path.dirname(__file__), "app.db")

        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                click.echo(f"Файл базы данных {db_path} удален")
            except Exception as e:
                click.echo(f"Ошибка удаления файла: {e}")
        else:
            click.echo("Файл базы данных не найден")


@app.cli.command("seed-demo")
def seed_demo_command():
    # демоданные, наполнение БД
    test_user = User.query.filter_by(username="demo").first()
    if not test_user:
        test_user = User(username="demo", role="operator")
        test_user.set_password("demo123")
        db.session.add(test_user)
        db.session.commit()
        click.echo("Создан пользователь demo, пароль demo123")

    if not test_user.profile:
        profile = UserProfile(
            user_id=test_user.id,
            age=25,
            weight=75.0,
            height=180.0,
            gender="male",
            activity_level=1.375,
        )
        profile.calculate_daily_norms()
        db.session.add(profile)
        db.session.commit()
        click.echo("Создан профиль для demo пользователя, пароль demo123")

    # примеры рационов (за 3 дня)
    p = Product.query.first()
    if p:
        for i in range(3):
            date = datetime.date.today() - datetime.timedelta(days=i)
            ration = Ration(user_id=test_user.id, date=date)
            db.session.add(ration)
            db.session.commit()

            item = RationItem(ration_id=ration.id, product_id=p.id, weight=200)
            db.session.add(item)
            db.session.commit()
        click.echo("Созданы демонстрационные рационы")
    else:
        click.echo("Сначала загрузите продукты (flask load-data)")
