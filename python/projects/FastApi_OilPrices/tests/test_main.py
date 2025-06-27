import pytest
from fastapi.testclient import TestClient
from FastApi_OilPrices.main import app, OilPrice, get_all_prices


# Mock storage
@pytest.fixture
def mock_storage():
    return [
        OilPrice(price_id=1, price_date='2025-01-01', price=22.22, euro_price=33.33),
        OilPrice(price_id=1, price_date='2025-01-02', price=44.44, euro_price=55.55)
    ]

# Override dependency
@pytest.fixture(autouse=True)
def ovverride_dependency(mock_storage):
    app.dependency_overrides[get_all_prices] = lambda: mock_storage
    yield
    app.dependency_overrides.clear()


# Tests

client = TestClient(app)

def test_query_item_by_price():
    response = client.get('/prices')
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_price_id():
    response = client.get('/prices/1')
    assert response.status_code == 200
    assert response.json()['price'] == 22.22

def test_create_price(mock_storage):
    new_price = {
        'price_date': '2025-01-03',
        'price': 66.66,
        'euro_price': 77.77
    }
    response = client.post('/prices', json=new_price)
    assert response.status_code == 200
    assert response.json()['price'] == 66.66
    assert len(mock_storage) == 3

def test_update_price(mock_storage):
    update = {'price': 11.11}
    response = client.put('/prices/1', json=update)
    assert response.status_code == 200
    assert response.json()['price'] == 11.11

def test_delete_price(mock_storage):
    response = client.delete('/prices/1')
    assert response.status_code == 200
    assert response.json()['price_id'] == 1
    assert len(mock_storage) == 1