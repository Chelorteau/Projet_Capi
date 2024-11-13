from flask import Flask, render_template, request, redirect, jsonify
import json
from utils import load_backlog, save_backlog, load_save, save_game, calculate_estimation

app = Flask(__name__)

players = []
current_mode = 'strict'
backlog = []
votes = {}
current_index = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    global players, current_mode
    if request.method == 'POST':
        players = request.form.getlist('players')
        current_mode = request.form['mode']
        return redirect('/game')
    return render_template('menu.html')

@app.route('/game')
def game():
    global backlog, current_index, votes
    if current_index >= len(backlog):
        save_backlog(backlog)
        return redirect('/results')
    feature = backlog[current_index]
    return render_template('game.html', feature=feature, players=players, votes=votes)

@app.route('/vote', methods=['POST'])
def vote():
    global votes, current_index, backlog, current_mode
    player = request.form['player']
    vote = request.form['vote']
    votes[player] = vote

    if len(votes) == len(players):
        estimation = calculate_estimation(votes, current_mode)
        if estimation is not None:
            backlog[current_index]['difficulty'] = estimation
            current_index += 1
            votes.clear()
        else:
            votes.clear()
    return redirect('/game')

@app.route('/results')
def results():
    return render_template('results.html', backlog=backlog)

@app.route('/save')
def save():
    save_game(players, current_mode, backlog, current_index)
    return "Partie sauvegardée avec succès"

@app.route('/load', methods=['POST'])
def load():
    global players, current_mode, backlog, current_index
    data = load_save()
    players = data['players']
    current_mode = data['mode']
    backlog = data['backlog']
    current_index = data['current_index']
    return redirect('/game')

if __name__ == '__main__':
    backlog = load_backlog()
    app.run(debug=True)
