import pytest
import mongomock
import bcrypt
from app import app, get_db, verifyPW, countTokens

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    client = mongomock.MongoClient()
    db = client.SentenceDB
    users = db["Users"]
    
    def mock_get_db():
        return users
    
    monkeypatch.setattr('app.get_db', mock_get_db)
    yield users

def test_register(client):
    response = client.post('/register', json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json == {"Message": "You have successfully Signed Up!"}

def test_store(client, mock_db):
    client.post('/register', json={"username": "testuser", "password": "testpass"})
    response = client.post('/store', json={"username": "testuser", "password": "testpass", "sentence": "This is a test sentence."})
    assert response.status_code == 200
    assert response.json == {"Message": "Sentence Saved Successfully!"}

def test_get(client, mock_db):
    client.post('/register', json={"username": "testuser", "password": "testpass"})
    client.post('/store', json={"username": "testuser", "password": "testpass", "sentence": "This is a test sentence."})
    response = client.post('/get', json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json["Message"] == "Sentence Retrieved Successfully!"
    assert response.json["Sentence"] == "This is a test sentence."

def test_invalid_password(client, mock_db):
    client.post('/register', json={"username": "testuser", "password": "testpass"})
    response = client.post('/store', json={"username": "testuser", "password": "wrongpass", "sentence": "This is a test sentence."})
    assert response.status_code == 302
    assert response.json == {"Message": "Something is not correct!"}

def test_no_tokens_left(client, mock_db):
    client.post('/register', json={"username": "testuser", "password": "testpass"})
    for _ in range(6):
        client.post('/store', json={"username": "testuser", "password": "testpass", "sentence": "This is a test sentence."})
    response = client.post('/store', json={"username": "testuser", "password": "testpass", "sentence": "Another sentence."})
    assert response.status_code == 301
    assert response.json == {"Message": "No Tokens left!"}
