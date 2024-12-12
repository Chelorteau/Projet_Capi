Documentation de l'Application Planning Poker

1. Vue d'Ensemble de l'Application
Description
L'application "Planning Poker" est une plateforme collaborative permettant aux utilisateurs de voter et d'estimer la complexité des tâches d'un projet. Elle utilise Flask en backend et un frontend dynamique basé sur HTML, JavaScript, et WebSocket (via Flask-SocketIO).
Fonctionnalités principales
•	Création et gestion de parties de Planning Poker.
•	Chargement de fonctionnalités à estimer via des fichiers JSON.
•	Discussions en temps réel via un chat intégré.
•	Calcul automatique des estimations selon différents modes (moyenne, médiane, etc.).
Technologies utilisées
•	Backend : Python (Flask, Flask-SocketIO).
•	Frontend : HTML5, JavaScript, CSS.
•	Base de données : JSON pour le stockage temporaire.
•	Tests : Pytest pour Python et Jest pour JavaScript.
________________________________________
2. Documentation Technique
Backend - Python
app.py
Gère les routes et les événements SocketIO :
•	Routes principales :
o	/create : Crée une nouvelle partie.
o	/join : Permet à un utilisateur de rejoindre une partie existante.
o	/game : Affiche l'interface de vote pour la fonctionnalité actuelle.
o	/results : Montre les résultats finaux avec les estimations.
o	/submit_vote : Soumet un vote pour une fonctionnalité.
•	Fonctions utilitaires :
o	generate_key() : Génère une clé unique pour chaque partie.
o	reset_game_data() : Initialise les données d'une nouvelle partie.
utils.py
Fournit des fonctions auxiliaires pour gérer les données :
•	load_backlog() : Charge une liste de fonctionnalités depuis backlog.json.
•	save_backlog(backlog) : Sauvegarde les fonctionnalités estimées dans result.json.
•	calculate_estimation(votes, mode) : Calcule l'estimation basée sur les votes des utilisateurs et le mode choisi.
________________________________________
Frontend - JavaScript
Chat (chat.html)
•	Gère les messages envoyés et reçus via WebSocket.
•	Fonctions principales :
o	sendMessage() : Envoie un message.
o	addMessage(content) : Affiche un message reçu dans le DOM.
Game Interface (game.html)
•	Gère la soumission des votes pour une fonctionnalité.
•	Fonctions principales :
o	submitVote(vote) : Soumet un vote via une requête POST.
o	nextFeature() : Passe à la fonctionnalité suivante.
Lobby (lobby.html)
•	Permet de copier la clé de la partie et de charger des fonctionnalités depuis un fichier JSON.
•	Fonctions principales :
o	uploadFeatures() : Envoie un fichier JSON pour ajouter des fonctionnalités.
o	copyToClipboard() : Copie la clé de la partie dans le presse-papier.
________________________________________
3. Guide d’Utilisation
Installation
1.	Clonez le dépôt :
git clone <url-du-depot>
cd <nom-du-projet>
2.	Installez les dépendances Python :
pip install -r requirements.txt
3.	Installez les dépendances Node.js pour les tests JavaScript :
npm install
Exécution de l'Application
1.	Lancez le backend Flask :
python app.py
2.	Accédez à l'application via :
http://127.0.0.1:5000  Pour la version locale ou la deuxième adresse affiché pour la version en ligne
Exécution des Tests
•	Tests Python :
pytest test_utils.py test_app.py
•	Tests JavaScript :
npm test
________________________________________
4. Structure du Projet
Projet_Capi/
├── app.py                  # Backend principal
├── utils.py                # Fonctions utilitaires
├── templates/              # Fichiers HTML
│   ├── chat.html
│   ├── create.html
│   ├── game.html
│   ├── join.html
│   ├── lobby.html
│   ├── results.html
│   └── index.html
├── static/                 # Ressources statiques (CSS, JS)
│   ├── styles.css
│   └── cartes		    # Fichier contenant les svg des cartes
├── __tests__/              # Tests JavaScript
│   ├── chat.test.js
│   ├── game.test.js
│   ├── lobby.test.js
├── test_utils.py           # Tests pour utils.py
├── test_app.py             # Tests pour app.py
├── requirements.txt        # Dépendances Python
├── package.json            # Dépendances Node.js
├── backlog.json            # Données d'entrée (exemple)
├── features.json           # Données d'exemple pour l'importation d'autres fichiers JSON
└── save.json               # Sauvegarde des parties
________________________________________
5. Points de Personnalisation
Modes de Calcul
•	Moyenne : Moyenne arithmétique des votes.
•	Médiane : Médiane des votes.
•	Majorité absolue : Valeur ayant plus de 50% des votes.
•	Unanimité : Tous les joueurs doivent voter la même valeur.
Fichiers JSON
•	backlog.json : Contient les fonctionnalités à estimer.
{
  "features": [
    { "name": "Feature 1", "description": "Description of feature 1" }
  ]
}
•	result.json : Contient les résultats des estimations après la partie.
