import json

def load_backlog():
    with open('backlog.json', 'r') as file:
        return json.load(file)['features']

def save_backlog(backlog):
    with open('result.json', 'w') as file:
        json.dump({'features': backlog}, file, indent=4)

def save_game(players, mode, backlog, current_index):
    save_data = {
        "players": players,
        "mode": mode,
        "current_index": current_index,
        "backlog": backlog
    }
    with open('save.json', 'w') as file:
        json.dump(save_data, file, indent=4)

def load_save():
    with open('save.json', 'r') as file:
        return json.load(file)

def calculate_estimation(votes, mode):
    estimates = list(map(int, votes.values()))

    if mode == 'strict':
        return estimates[0] if all(v == estimates[0] for v in estimates) else None
    elif mode == 'moyenne':
        return sum(estimates) // len(estimates)
    elif mode == 'médiane':
        estimates.sort()
        return estimates[len(estimates) // 2]
    elif mode == 'majorité_absolue':
        return max(set(estimates), key=estimates.count) if estimates.count(max(set(estimates), key=estimates.count)) > len(estimates) // 2 else None
    elif mode == 'majorité_relative':
        return max(set(estimates), key=estimates.count)

    return None
