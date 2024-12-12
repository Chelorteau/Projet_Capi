# test_utils.py
import pytest
import json
from utils import load_backlog, save_backlog, calculate_estimation, save_game, load_save

# Test load_backlog
def test_load_backlog(tmp_path):
    test_file = tmp_path / "backlog.json"
    test_data = {"features": [{"name": "Feature 1", "description": "Description 1"}]}
    with open(test_file, "w") as f:
        json.dump(test_data, f)

    backlog = load_backlog(file_path=str(test_file))
    assert backlog == test_data["features"]

# Test save_backlog
def test_save_backlog(tmp_path):
    test_file = tmp_path / "result.json"
    backlog = [{"name": "Feature 1", "description": "Description 1"}]
    save_backlog(backlog, file_path=str(test_file))

    with open(test_file, "r") as f:
        data = json.load(f)
    assert data["features"] == backlog


# Test calculate_estimation
@pytest.mark.parametrize("votes, mode, expected", [
    ({"player1": "3", "player2": "5"}, "moyenne", 4),
    ({"player1": "3", "player2": "5"}, "médiane", 4),
    ({"player1": "3", "player2": "3"}, "unanimité", 3),
    ({"player1": "3", "player2": "5"}, "majorité_relative", 3),
])
def test_calculate_estimation(votes, mode, expected):
    assert calculate_estimation(votes, mode) == expected

# Test save_game
# Modifiez save_game dans utils.py
def save_game(players, mode, backlog, current_index, file_path='save.json'):
    creator = next((player for player, info in players.items() if info.get('role') == 'creator'), None)
    save_data = {
        "players": players,
        "mode": mode,
        "current_index": current_index,
        "backlog": backlog,
        "creator": creator
    }
    with open(file_path, 'w') as file:
        json.dump(save_data, file, indent=4)

# Test modifié
def test_save_game(tmp_path):
    test_file = tmp_path / "save.json"
    players = {"player1": {"ready": True}, "player2": {"ready": False}}
    mode = "moyenne"
    backlog = [{"name": "Feature 1", "description": "Description 1"}]
    current_index = 0
    save_game(players, mode, backlog, current_index, file_path=str(test_file))

    with open(test_file, "r") as f:
        data = json.load(f)
    assert data["players"] == players
    assert data["mode"] == mode
    assert data["backlog"] == backlog
    assert data["current_index"] == current_index

# Test load_save
def test_load_save(tmp_path):
    test_file = tmp_path / "save.json"
    save_data = {
        "players": {"player1": {"ready": True}},
        "mode": "moyenne",
        "backlog": [{"name": "Feature 1", "description": "Description 1"}],
        "current_index": 0,
    }
    with open(test_file, "w") as f:
        json.dump(save_data, f)

    loaded_data = load_save(file_path=str(test_file))
    assert loaded_data == save_data

