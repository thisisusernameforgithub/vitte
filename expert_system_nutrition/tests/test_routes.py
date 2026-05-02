# -*- coding: utf-8 -*-
import datetime


def test_product_search(client, auth_user):
    client.post("/api/login", json={"username": "testuser", "password": "testpass"})
    response = client.get("/api/products?q=App")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert data[0]["name"] == "Apple"


def test_ration_management(client, auth_user, app):
    client.post("/api/login", json={"username": "testuser", "password": "testpass"})

    from app.models import Product

    with app.app_context():
        p = Product.query.first()
        p_id = p.id

    response = client.post(
        "/api/rations/items",
        json={"product_id": p_id, "weight": 200, "date": "2026-05-02"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["weight"] == 200

    item_id = data["items"][0]["id"]
    response = client.delete(f"/api/rations/items/{item_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["items"]) == 0


def test_evaluate_empty_ration(client, auth_user):
    client.post("/api/login", json={"username": "testuser", "password": "testpass"})
    response = client.post("/api/rations/evaluate", json={"date": "2026-05-02"})
    assert response.status_code == 404
