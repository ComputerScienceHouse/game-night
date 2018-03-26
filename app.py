from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from re import compile, IGNORECASE
from random import choice

app = Flask(__name__)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
app.url_map.strict_slashes = False

games = MongoClient().game_night.games

@app.route('/api')
def api():
    return jsonify(get_games())

@app.route('/api/random')
def api_random():
    return jsonify(choice(get_games()))

@app.route('/api/count')
def api_count():
    return jsonify(get_games(True))

def get_games(count = False):
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
    if count:
        return games.count(filters)
    return list(games.find(filters, {'_id': False}).sort([('sortName', 1)]))

def get_players():
    return list(games.aggregate([{'$group': {'_id': False, 'max': {'$max': '$max_players'}, 'min': {'$min': '$min_players'}}}]))[0]

@app.route('/')
def index():
    return render_template('index.html', games = get_games(), players = get_players())

@app.route('/random')
def random():
    return render_template('index.html', games = [choice(get_games())], players = get_players())