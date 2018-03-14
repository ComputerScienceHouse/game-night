from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from re import compile, IGNORECASE
from random import choice

app = Flask(__name__)
app.url_map.strict_slashes = False

games = MongoClient().game_night.games

@app.route('/api', methods = ['GET'])
def all():
    return jsonify(get_games())

def get_games():
    filters = {}
    try:
        filters['name'] = compile(request.args['name'], IGNORECASE)
    except:
        pass
    try:
        players = int(request.args['players'])
        filters['$and'] = [{'min_players': {'$lte': players}}, {'max_players': {'$gte': players}}]
    except:
        pass
    return list(games.find(filters, {'_id': False}).sort([('sortName', 1)]))

@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html', games = get_games())

@app.route('/api/random', methods = ['GET'])
def random():
    return jsonify(choice(get_games()))