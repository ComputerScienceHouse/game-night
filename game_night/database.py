from pymongo import MongoClient
from boto3 import client
from os import environ
from re import compile, error, escape, IGNORECASE, sub
from flask import abort, request, session
from uuid import uuid4
from functools import wraps
from game_night.game import Game

_game_night = MongoClient().game_night
_api_keys = _game_night.api_keys
_gamemasters = _game_night.gamemasters
_games = _game_night.games
_submissions = _game_night.submissions

_s3 = client('s3', aws_access_key_id = environ['GAME_NIGHT_S3_KEY'], aws_secret_access_key= environ['GAME_NIGHT_S3_SECRET'])

def _create_filters():
    filters = {}
    try:
        filters['name'] = compile(request.args['name'], IGNORECASE)
    except error:
        filters['name'] = compile(escape(request.args['name']), IGNORECASE)
    except:
        pass
    try:
        players = int(request.args['players'])
        filters['$and'] = [{'min_players': {'$lte': players}}, {'max_players': {'$gte': players}}]
    except:
        pass
    return filters

def generate_api_key(write = False):
    uuid = str(uuid4())
    _api_keys.insert_one({'key': uuid, 'write': write})
    return uuid

def get_count():
    return _games.count(_create_filters())

def get_game(name):
    return _games.find_one({'name': name})

def get_games():
    return _games.find(_create_filters(), {'_id': False}).sort([('sort_name', 1)])

def get_owners():
    owners = _games.distinct('owner', _create_filters())
    owners.sort()
    return owners

def get_players():
    return _games.aggregate([{'$group': {'_id': False, 'max': {'$max': '$max_players'}, 'min': {'$min': '$min_players'}}}]).next()

def get_random_games(sample_size):
    return _games.aggregate([{'$match': _create_filters()}, {'$sample': {'size': sample_size}}, {'$project': {'_id': False}}])

def get_submissions(gamemaster = False):
    return _submissions.find() if gamemaster else _submissions.find({'username': session['userinfo']['preferred_username']})

def is_gamemaster():
    return _gamemasters.count({'username': session['userinfo']['preferred_username']})

def _prepare_game(game):
    del game['image']
    if game['owner'] == 'CSH':
        del game['owner']
    game['sort_name'] = sub('(A|(An)|(The)) ', '', game['name'])

def require_gamemaster(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not is_gamemaster():
            abort(403)
        return function(*args, **kwargs)
    return wrapper

def require_read_key(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            if _api_keys.find({'key': request.headers['Authorization'][7:]}).count() == 0:
                abort(403)
        except:
            abort(403)
        return function(*args, **kwargs)
    return wrapper

def require_write_key(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            key = _api_keys.find_one({'key': request.headers['Authorization'][7:]})
            if not key['write']:
                abort(403)
        except:
            abort(403)
        return function(*args, **kwargs)
    return wrapper

def submit_game():
    game = Game()
    if game.validate():
        game = game.data
        _s3.upload_fileobj(game['image'], environ['GAME_NIGHT_S3_BUCKET'], game['name'] + '.jpg')
        _prepare_game(game)
        _games.replace_one({'name': game['name']}, game, True)
        _update_new_games()
        return True
    return False

def _update_new_games():
    _games.update_many({'new': True}, {'$unset': {'new': 1}})
    for game in _games.find().sort([('_id', -1)]).limit(10):
        _games.update_one({'name': game['name']}, {'$set': {'new': True}})