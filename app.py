from flask import Flask, render_template, request, redirect, session, url_for
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
        'players': [],
        'backlog': load_backlog(),
        'votes': {},
        'current_index': 0,
        'mode': 'moyenne'
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        game_key = generate_key()
        games[game_key] = reset_game_data()
        return redirect(f'/lobby/{game_key}')
    return render_template('create.html')


@app.route('/lobby/<game_key>')
def lobby(game_key):
    if game_key not in games:
        return "Partie non trouvée.", 404
    return render_template('lobby.html', game_key=game_key, players=games[game_key]['players'])

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        game_key = request.form['game_key']
        player_name = request.form['player_name']
        if game_key in games:
            if player_name not in games[game_key]['players']:
                games[game_key]['players'].append(player_name)
            session['game_key'] = game_key
            session['player_name'] = player_name
            return redirect(f'/lobby/{game_key}')
        else:
            return "Clé invalide.", 404
    return render_template('join.html')

@app.route('/player/<player_name>')
def player(player_name):
    game_key = session.get('game_key')
    if not game_key or player_name not in games[game_key]['players']:
        return redirect('/')

    game_data = games[game_key]
    if game_data['current_index'] >= len(game_data['backlog']):
        return redirect('/results')

    feature = game_data['backlog'][game_data['current_index']]
    return render_template('player.html', player=player_name, feature=feature, game_key=game_key)

@app.route('/submit_vote/<player_name>', methods=['POST'])
def submit_vote(player_name):
    game_key = session.get('game_key')
    if not game_key or player_name not in games[game_key]['players']:
        return redirect('/')

    game_data = games[game_key]
    vote = request.form['vote']
    
    if vote.isdigit():
        game_data['votes'][player_name] = int(vote)
    else:
        game_data['votes'][player_name] = vote

    if len(game_data['votes']) == len(game_data['players']):
        estimation = calculate_estimation(game_data['votes'], game_data['mode'])
        if estimation is not None:
            game_data['backlog'][game_data['current_index']]['difficulty'] = estimation
            game_data['backlog'][game_data['current_index']]['votes'] = game_data['votes'].copy()
            game_data['current_index'] += 1
            game_data['votes'].clear()
    
    if game_data['current_index'] >= len(game_data['backlog']):
        save_backlog(game_data['backlog'])
        return redirect('/results')

    next_player_index = (game_data['players'].index(player_name) + 1) % len(game_data['players'])
    next_player = games[game_key]['players'][next_player_index]
    return redirect(f'/player/{next_player}')

@app.route('/results')
def results():
    game_key = session.get('game_key')
    if not game_key:
        return redirect('/')
    game_data = games[game_key]
    return render_template('results.html', backlog=game_data['backlog'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
