import requests

BASE_URL = "http://localhost:8002"  # docker run -p 8002:8000

def test_get_todos_empty():
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_todo():
    todo = {
        "id": 1,
        "title": "Test Todo",
        "description": "Testing creation",
        "deadline": "2025-04-11",
        "completed": False
    }
    response = requests.post(f"{BASE_URL}/todos", json=todo)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Todo"

def test_get_todos_with_items():
    response = requests.get(f"{BASE_URL}/todos")
    assert response.status_code == 200
    todos = response.json()
    assert any(todo["title"] == "Test Todo" for todo in todos)

def test_update_todo():
    updated_todo = {
        "id": 1,
        "title": "Updated Title",
        "description": "Updated description",
        "deadline": "2025-05-01",
        "completed": True
    }
    response = requests.put(f"{BASE_URL}/todos/1", json=updated_todo)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

def test_delete_todo():
    response = requests.delete(f"{BASE_URL}/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"
