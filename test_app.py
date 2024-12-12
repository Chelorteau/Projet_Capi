# test_app.py
import pytest
from flask import session
from app import app, socketio

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Bienvenue au Planning Poker" in response.data

def test_create_game(client):
    response = client.post('/create', data={"player_name": "Alice", "mode": "moyenne"})
    assert response.status_code == 302  # Redirection
    assert session.get("player_name") == "Alice"

def test_join_game(client):
    # Ajouter un jeu fictif pour permettre le test
    from app import games
    games["ABC123"] = {"players": {}, "creator": "Bob"}
    
    response = client.post('/join', data={"game_key": "ABC123", "player_name": "Bob"})
    assert response.status_code in [200, 302]

def test_submit_vote(client):
    with client.session_transaction() as sess:
        sess["game_key"] = "GAME123"
        sess["player_name"] = "Alice"
    
    # Ajouter un jeu fictif
    from app import games
    games["GAME123"] = {
        "players": {"Alice": {"ready": True}},
        "votes": {},
        "current_index": 0,
        "backlog": [{"name": "Feature 1", "description": "Description 1"}]
    }
    
    response = client.post('/submit_vote', data={"vote": "5"})
    assert response.status_code == 200

def test_start_game(client):
    from app import games
    games["GAME123"] = {
        "players": {"Alice": {"ready": True, "role": "creator"}},
        "creator": "Alice"
    }
    
    with client.session_transaction() as sess:
        sess["game_key"] = "GAME123"
        sess["player_name"] = "Alice"

    response = client.post('/start_game')
    assert response.status_code == 200
