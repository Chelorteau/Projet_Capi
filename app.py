from flask import Flask, render_template, request, redirect, session, jsonify
import random
import string
import json
from utils import load_backlog, save_backlog, calculate_estimation

app = Flask(__name__)
app.secret_key = 'supersecretkey'

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
        'ready': {},
        'all_ready': False
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
        games[game_key]['players'][player_name] = {'ready': False}
        games[game_key]['mode'] = mode
        
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

@app.route('/lobby/<game_key>')
def lobby(game_key):
    if game_key not in games:
        return "Partie non trouvée.", 404

    return render_template('lobby.html', game_key=game_key, players=games[game_key]['players'])

@app.route('/toggle_ready', methods=['POST'])
def toggle_ready():
    game_key = session.get('game_key')
    player_name = session.get('player_name')
    
    if not game_key or not player_name:
        return jsonify({'error': 'Session invalide'}), 400

    if game_key not in games:
        return jsonify({'error': 'Partie introuvable'}), 404

    game_data = games[game_key]
    game_data['players'][player_name]['ready'] = not game_data['players'][player_name]['ready']

    all_ready = all(player['ready'] for player in game_data['players'].values())
    game_data['all_ready'] = all_ready

    return jsonify({'all_ready': all_ready})

@app.route('/check_all_ready/<game_key>', methods=['GET'])
def check_all_ready(game_key):
    game_data = games.get(game_key, {})
    return jsonify({'all_ready': game_data.get('all_ready', False)})

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
    return render_template('game.html', feature=feature, game_key=game_key, player_name=player_name, players=game_data['players'], votes=game_data['votes'])

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    game_key = session.get('game_key')
    player_name = session.get('player_name')
    vote = request.form.get('vote')

    if game_key and player_name:
        game_data = games.get(game_key)
        if not game_data:
            return jsonify({'error': 'Partie introuvable'}), 404

        game_data['votes'][player_name] = vote

        if len(game_data['votes']) == len(game_data['players']):
            game_data['all_ready'] = True

            estimation = calculate_estimation(game_data['votes'], game_data['mode'])
            if estimation is not None:
                game_data['backlog'][game_data['current_index']]['difficulty'] = estimation
                game_data['backlog'][game_data['current_index']]['votes'] = game_data['votes'].copy()
                game_data['current_index'] += 1
                game_data['votes'].clear()
                game_data['all_ready'] = False

            return jsonify({'all_ready': True, 'next_feature': True})
        
        return jsonify({'all_ready': False, 'next_feature': False})
    
    return jsonify({'error': 'Invalid request'})




@app.route('/check_votes/<game_key>', methods=['GET'])
def check_votes(game_key):
    game_data = games.get(game_key, {})
    return jsonify({
        'votes': game_data.get('votes', {}),
        'all_ready': game_data.get('all_ready', False),
        'current_index': game_data.get('current_index', 0)
    })



@app.route('/results')
def results():
    game_key = session.get('game_key')
    if not game_key:
        return redirect('/')
    
    game_data = games[game_key]
    return render_template('results.html', backlog=game_data['backlog'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
