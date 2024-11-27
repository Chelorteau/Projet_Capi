from flask import Flask, render_template, request, redirect, session, jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room

import random
import string
import json
from utils import load_backlog, save_backlog, calculate_estimation, load_save, save_game

app = Flask(__name__)
app.secret_key = 'supersecretkey'

socketio = SocketIO(app)

chat_logs = {}

@socketio.on("connect")
def on_connect():
    print("Un utilisateur s'est connecté.")

@socketio.on("message")
def handle_message(data):
    game_key = data.get('game_key')
    message = data.get('message')
    player_name = session.get('player_name', 'Anonyme')

    if not game_key or not message:
        return

    if game_key not in chat_logs:
        chat_logs[game_key] = []
    chat_logs[game_key].append({'player': player_name, 'message': message})

    emit('chat_message', {'player': player_name, 'message': message}, room=game_key)

@socketio.on("join_room")
def on_join(data):
    game_key = data.get('game_key')
    player_name = session.get('player_name', 'Un joueur')

    if game_key and game_key in games:
        join_room(game_key)

        if player_name not in games[game_key]['players']:
            games[game_key]['players'][player_name] = {'ready': False}

        #message de bienvenue en commentaire car duplication
        #emit('chat_message', {'player': 'Système', 'message': f"{player_name} a rejoint la partie."}, room=game_key)

        emit('player_joined', {'players': list(games[game_key]['players'].keys())}, room=game_key)



@socketio.on("leave_room")
def on_leave(data):
    game_key = data.get('game_key')
    if game_key and game_key in games:
        leave_room(game_key)
        emit('chat_message', {'player': 'Système', 'message': f"{session.get('player_name', 'Un joueur')} a quitté la partie."}, room=game_key)


games = {}

def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def reset_game_data():
    return {
        'players': {},
        'backlog': load_backlog(),
        'votes': {},
        'current_index': 0,
        'mode': 'moyenne',
        'creator': None,
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        player_name = request.form.get('player_name')
        mode = request.form.get('mode')

        if not player_name or not mode:
            return "Nom du joueur et mode requis", 400

        game_key = generate_key()
        games[game_key] = reset_game_data()
        games[game_key]['players'][player_name] = {'ready': False, 'role' : 'creator'}
        games[game_key]['mode'] = mode
        games[game_key]['creator'] = player_name

        session['game_key'] = game_key
        session['player_name'] = player_name

        return redirect(f'/lobby/{game_key}')
    return render_template('create.html')


@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        game_key = request.form.get('game_key')
        player_name = request.form.get('player_name')
        if game_key in games:
            if player_name not in games[game_key]['players']:
                games[game_key]['players'][player_name] = {'ready': False}
            session['game_key'] = game_key
            session['player_name'] = player_name
            return redirect(f'/lobby/{game_key}')
        else:
            return "Clé invalide.", 404
    return render_template('join.html')

@app.route('/load', methods=['POST'])
def load():
    try:
        save_data = load_save()
        game_key = generate_key()

        games[game_key] = {
            'players': save_data['players'],
            'mode': save_data['mode'],
            'current_index': save_data['current_index'],
            'backlog': save_data['backlog'],
            'votes': {},
            'creator': save_data.get('creator')
        }

        session['game_key'] = game_key
        session['player_name'] = save_data.get('creator')
        return redirect(f'/lobby/{game_key}')
    except Exception as e:
        print(f"Erreur lors du chargement de la partie : {e}")
        return "Erreur lors du chargement de la partie", 500



@app.route('/lobby/<game_key>')
def lobby(game_key):
    if game_key not in games:
        return "Partie non trouvée.", 404

    creator = games[game_key]['creator']
    return render_template('lobby.html', game_key=game_key, players=games[game_key]['players'], creator=creator)

@app.route('/start_game', methods=['POST'])
def start_game():
    game_key = session.get('game_key')
    player_name = session.get('player_name')

    if not game_key or not player_name:
        return jsonify({'error': 'Session invalide'}), 400

    if game_key not in games:
        return jsonify({'error': 'Partie introuvable'}), 404

    if games[game_key]['creator'] != player_name:
        return jsonify({'error': 'Seul le créateur peut démarrer la partie'}), 403

    socketio.emit('redirect', {'redirect_url': '/game'}, room=game_key)
    return jsonify({'success': True})


@app.route('/game')
def game():
    game_key = session.get('game_key')
    player_name = session.get('player_name')

    if not game_key or not player_name or game_key not in games:
        return redirect('/join')

    game_data = games[game_key]

    if game_data['current_index'] >= len(game_data['backlog']):
        return redirect('/results')

    feature = game_data['backlog'][game_data['current_index']]
    player_role = 'creator' if game_data['players'].get(player_name, {}).get('role') == 'creator' else 'player'

    return render_template(
        'game.html',
        feature=feature,
        game_key=game_key,
        player_name=player_name,
        player_role=player_role,
        players=game_data['players'],
        votes=game_data['votes']
    )

@app.route('/next_feature', methods=['POST'])
def next_feature():
    try:
        game_key = session.get('game_key')
        player_name = session.get('player_name')

        if not game_key or not player_name:
            return jsonify({'error': 'Session invalide'}), 400

        game_data = games.get(game_key)
        if not game_data:
            return jsonify({'error': 'Partie introuvable'}), 404

        if game_data['players'].get(player_name, {}).get('role') != 'creator':
            return jsonify({'error': 'Permission refusée'}), 403

        if all(vote == 'cafe' for vote in game_data['votes'].values()):
            save_game(
                players=game_data['players'],
                mode=game_data['mode'],
                backlog=game_data['backlog'],
                current_index=game_data['current_index']
            )

            socketio.emit('redirect', {'redirect_url': '/results'}, room=game_key)
            return jsonify({'completed': True, 'reason': 'Tous les joueurs ont voté café'})

        estimation = calculate_estimation(game_data['votes'], game_data['mode'])

        feature = game_data['backlog'][game_data['current_index']]
        feature['votes'] = game_data['votes'].copy()
        if estimation is not None:
            feature['difficulty'] = estimation

        game_data['current_index'] += 1
        game_data['votes'].clear()

        if game_data['current_index'] >= len(game_data['backlog']):
            save_game(
                players=game_data['players'],
                mode=game_data['mode'],
                backlog=game_data['backlog'],
                current_index=game_data['current_index']
            )
            socketio.emit('redirect', {'redirect_url': '/results'}, room=game_key)
            return jsonify({'completed': True})

        next_feature = game_data['backlog'][game_data['current_index']]
        socketio.emit('update_feature', {'feature': next_feature}, room=game_key)

        return jsonify({'success': True, 'next_feature': next_feature})

    except Exception as e:
        print(f"Erreur dans next_feature : {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500


@app.route('/results')
def results():
    game_key = session.get('game_key')
    if not game_key:
        return redirect('/')

    game_data = games.get(game_key)
    if not game_data:
        return "Partie introuvable", 404

    return render_template('results.html', backlog=game_data['backlog'], game_key=game_key)


@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    game_key = session.get('game_key')
    player_name = session.get('player_name')
    vote = request.form.get('vote')

    if not game_key or not player_name or not vote:
        return jsonify({'error': 'Données invalides'}), 400

    game_data = games.get(game_key)
    if not game_data:
        return jsonify({'error': 'Partie introuvable'}), 404

    if vote not in ['?', 'cafe'] and not vote.isdigit():
        return jsonify({'error': 'Vote non valide'}), 400

    game_data['votes'][player_name] = vote

    feature = game_data['backlog'][game_data['current_index']]
    feature_name = feature['name']

    message = f"{player_name} a voté pour la fonctionnalité '{feature_name}' avec '{vote}'."
    chat_logs.setdefault(game_key, []).append({'player': 'Système', 'message': message})
    socketio.emit('chat_message', {'player': 'Système', 'message': message}, room=game_key)

    return jsonify({'success': True, 'votes': game_data['votes']})



@app.route('/upload_features', methods=['POST'])
def upload_features():
    game_key = session.get('game_key')
    player_name = session.get('player_name')

    if not game_key or game_key not in games:
        return jsonify({'error': 'Partie introuvable'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400

    file = request.files['file']
    try:
        data = json.load(file)
        if not isinstance(data, list) or not all('name' in f and 'description' in f for f in data):
            raise ValueError("Format de fichier invalide")
        
        games[game_key]['backlog'] = data

        message = f"{player_name} a importé un nouveau fichier JSON avec {len(data)} fonctionnalités."
        chat_logs.setdefault(game_key, []).append({'player': 'Système', 'message': message})
        socketio.emit('chat_message', {'player': 'Système', 'message': message}, room=game_key)

        return jsonify({'success': True, 'features': data})
    except Exception as e:
        return jsonify({'error': f"Erreur lors de l'importation : {e}"}), 400



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)