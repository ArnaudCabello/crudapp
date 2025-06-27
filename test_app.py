import pytest
from app import app, db
import os


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@db:3306/flaskdb'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_user(client):
    response = client.post('/api/users', json={
        'name': 'John Doe',
        'age': 30,
        'birthstate': 'Ohio'
    })
    assert response.status_code == 201
    assert response.get_json()['message'] == 'User created'

def test_get_users(client):
    # Add test user first
    client.post('/api/users', json={
        'name': 'Jane Doe',
        'age': 25,
        'birthstate': 'Texas'
    })
    response = client.get('/api/users')
    assert response.status_code == 200
    users = response.get_json()
    assert isinstance(users, list)
    assert len(users) > 0

def test_update_user(client):
    # Create user
    res = client.post('/api/users', json={
        'name': 'Alex',
        'age': 20,
        'birthstate': 'Florida'
    })
    user_id = res.get_json()['id']

    # Update user
    response = client.put(f'/api/users/{user_id}', json={
        'name': 'Alex Smith',
        'age': 21
    })
    assert response.status_code == 200
    assert response.get_json()['message'] == 'User updated'

def test_delete_user(client):
    res = client.post('/api/users', json={
        'name': 'Bob',
        'age': 40,
        'birthstate': 'Nevada'
    })
    user_id = res.get_json()['id']

    response = client.delete(f'/api/users/{user_id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'User deleted'
