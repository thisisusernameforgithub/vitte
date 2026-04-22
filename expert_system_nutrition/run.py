# -*- coding: utf-8 -*-

# Cкрипт для запуска приложения

import os
import pandas as pd
import click
from app import create_app, db
from app.models import Product

# cоздаем экземпляр приложения
app = create_app()


@app.cli.command("load-data")
def load_data_command():
    # загрузка датасета
    import csv

    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "ABBREV_with_CLASS.csv"
    )

    if not os.path.exists(csv_path):
        click.echo(f"Ошибка: файл {csv_path} не найден")
        return

    click.echo("Загрузка из датасета ...")

    try:
        db.session.query(Product).delete()

        products_to_add = []
        processed_names = set()
        skipped_rows = 0

        with open(csv_path, mode="r", encoding="utf-8") as infile:
            reader = csv.reader(infile, delimiter=";")
            next(reader, None)

            # очистка датасета
            for row in reader:
                try:
                    if len(row) < 8:
                        skipped_rows += 1
                        continue

                    name = row[2].strip()

                    if not name or name in processed_names:
                        skipped_rows += 1
                        continue

                    calories = float(row[4].replace(",", "."))
                    proteins = float(row[5].replace(",", "."))
                    fats = float(row[6].replace(",", "."))
                    carbs = float(row[7].replace(",", "."))

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


if __name__ == "__main__":
    app.run(debug=True)
