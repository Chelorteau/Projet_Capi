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
    estimates = [v for v in votes.values() if v.isdigit()]

    if not estimates:
        return None

    estimates = list(map(int, estimates))

    if mode == 'moyenne':
        return round(sum(estimates) / len(estimates))
    elif mode == 'médiane':
        estimates.sort()
        mid = len(estimates) // 2
        return estimates[mid] if len(estimates) % 2 != 0 else (estimates[mid - 1] + estimates[mid]) // 2
    elif mode == 'majorité_absolue':
        most_common = max(set(estimates), key=estimates.count)
        return most_common if estimates.count(most_common) > len(estimates) // 2 else None
    elif mode == 'majorité_relative':
        return max(set(estimates), key=estimates.count)

    return None


