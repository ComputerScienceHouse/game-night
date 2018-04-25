from pymongo import MongoClient
from re import compile, IGNORECASE
from flask import request, session

game_night = MongoClient().game_night
gamemasters = game_night.gamemasters
games = game_night.games
submissions = game_night.submissions

def create_filters():
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
    return filters

def get_count():
    return games.count(create_filters())

def get_games():
    return games.find(create_filters(), {'_id': False}).sort([('sort_name', 1)])

def get_owners():
    owners = games.distinct('owner', create_filters())
    owners.sort()
    return owners

def get_players():
    return games.aggregate([{'$group': {'_id': False, 'max': {'$max': '$max_players'}, 'min': {'$min': '$min_players'}}}]).next()

def get_random_game():
    try:
        return games.aggregate([{'$match': create_filters()}, {'$sample': {'size': 1}}, {'$project': {'_id': False}}]).next()
    except:
        return None

def get_submissions(gamemaster = False):
    return submissions.find() if gamemaster else submissions.find({'username': session['userinfo']['preferred_username']})

def is_gamemaster():
    return gamemasters.count({'username': session['userinfo']['preferred_username']})