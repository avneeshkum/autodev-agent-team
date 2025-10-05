import pytest
from fastapi.testclient import TestClient
from backend import app

client = TestClient(app)

@pytest.mark.parametrize("num1,num2,operation,expected", [
    (2, 3, "+", 5),
    (10, 5, "-", 5),
    (4, 6, "*", 24),
    (15, 3, "/", 5),
    (0.1, 0.2, "+", 0.3),
    (7, 0, "-", 7),
    (2.5, 4, "*", 10),
    (10, 4, "/", 2.5),
    (1, 1, "+", 2),
    (100, 50, "/", 2),
])
def test_valid_operations(num1, num2, operation, expected):
    payload = {"num1": num1, "num2": num2, "operation": operation}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == expected

def test_division_by_zero():
    payload = {"num1": 10, "num2": 0, "operation": "/"}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 400
    assert "Division by zero" in response.json()["detail"]

def test_unsupported_operation():
    payload = {"num1": 5, "num2": 2, "operation": "%"}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 400
    assert "Unsupported operation" in response.json()["detail"]

def test_negative_numbers():
    payload = {"num1": -5, "num2": 3, "operation": "+"}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == -2

def test_large_numbers():
    payload = {"num1": 1e10, "num2": 1e10, "operation": "*"}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == 1e20

def test_missing_field():
    payload = {"num1": 5, "operation": "+"}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 422

def test_invalid_data_types():
    payload = {"num1": "five", "num2": 10, "operation": "+"}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 422

@pytest.mark.parametrize("num1,num2,operation", [
    (1, 2, "++"),
    (3, 4, "**"),
    (5, 6, "abc"),
    (7, 8, ""),
])
def test_invalid_operation_values(num1, num2, operation):
    payload = {"num1": num1, "num2": num2, "operation": operation}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 400
    assert "Unsupported operation" in response.json()["detail"]

def test_cors_headers():
    response = client.options("/calculate")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

def test_floating_point_precision():
    payload = {"num1": 0.1, "num2": 0.2, "operation": "+"}
    response = client.post("/calculate", json=payload)
    assert response.status_code == 200
    result = response.json()["result"]
    assert abs(result - 0.3) < 1e-10