import pytest
from rest_framework.test import APIClient
from oilprices.models import OilPrice
from datetime import date


@pytest.mark.django_db()
def test_get_all_prices():
    client = APIClient()

    OilPrice.objects.create(
        price_date = date(2024, 1, 1),
        price = 100,
        euro_price = 110
    )

    response = client.get('/api/prices/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["price"] == 100


@pytest.mark.django_db
def test_get_price_by_id():
    client = APIClient()

    price = OilPrice.objects.create(
        price_date=date(2024, 1, 2),
        price=90,
        euro_price=99
    )

    response = client.get(f"/api/prices/{price.id}/")
    assert response.status_code == 200
    assert response.data["id"] == price.id
    assert response.data["price"] == 90


@pytest.mark.django_db
def test_get_price_not_found():
    client = APIClient()

    response = client.get("/api/prices/999/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_create_price():
    client = APIClient()

    payload = {
        "price_date": "2024-02-01",
        "price": 80,
        "euro_price": 88
    }

    response = client.post("/api/prices/", payload, format="json")
    assert response.status_code == 201
    assert OilPrice.objects.count() == 1
    assert response.data["price"] == 80


@pytest.mark.django_db
def test_update_price():
    client = APIClient()

    price = OilPrice.objects.create(
        price_date=date(2024, 1, 3),
        price=70,
        euro_price=77
    )

    payload = {
        "price_date": "2024-01-10",
        "price": 75,
        "euro_price": 82.5
    }

    response = client.put(
        f"/api/prices/{price.id}/",
        payload,
        format="json"
    )

    assert response.status_code == 200
    assert response.data["price"] == 75


@pytest.mark.django_db
def test_delete_price():
    client = APIClient()

    price = OilPrice.objects.create(
        price_date=date(2024, 1, 4),
        price=60,
        euro_price=66
    )

    response = client.delete(f"/api/prices/{price.id}/")

    assert response.status_code == 204
    assert OilPrice.objects.count() == 0


# If you want to go next level:

# FactoryBoy for test data

# Auth tests

# Filtering tests

# Performance tests

# CI (GitHub Actions)