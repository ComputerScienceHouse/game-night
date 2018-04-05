from pymongo import MongoClient
from re import compile, IGNORECASE

games = MongoClient().game_night.games

def create_filters(request):
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

def get_count(request):
    return games.count(create_filters(request))

def get_games(request):
    return list(games.find(create_filters(request), {'_id': False}).sort([('sortName', 1)]))

def get_players():
    return list(games.aggregate([{'$group': {'_id': False, 'max': {'$max': '$max_players'}, 'min': {'$min': '$min_players'}}}]))[0]