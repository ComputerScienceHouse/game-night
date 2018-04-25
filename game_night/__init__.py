from flask import Flask, jsonify, render_template
from os import environ
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from game_night.db import get_count, get_games, get_owners, get_players, get_random_game, get_submissions, is_gamemaster

app = Flask(__name__)
config = {
    'PREFERRED_URL_SCHEME': environ.get('GAME_NIGHT_URL_SCHEME', 'https'),
    'SECRET_KEY': environ['GAME_NIGHT_SECRET_KEY'],
    'SERVER_NAME': environ['GAME_NIGHT_SERVER_NAME']
}
app.config.update(config)
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
app.url_map.strict_slashes = False

client_info = {
    'client_id': environ['GAME_NIGHT_CLIENT_ID'],
    'client_secret': environ['GAME_NIGHT_CLIENT_SECRET']
}
auth = OIDCAuthentication(app, client_registration_info = client_info, issuer = environ['GAME_NIGHT_ISSUER'])

@app.route('/api')
@auth.oidc_auth
def api():
    return jsonify(list(get_games()))

@app.route('/api/count')
@auth.oidc_auth
def api_count():
    return jsonify(get_count())

@app.route('/api/owners')
@auth.oidc_auth
def api_owners():
    return jsonify(get_owners())

@app.route('/api/random')
@auth.oidc_auth
def api_random():
    return jsonify(get_random_game())

@app.route('/')
@auth.oidc_auth
def index():
    return render_template('index.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], gamemaster = is_gamemaster(), games = get_games(), players = get_players())

@app.route('/random')
@auth.oidc_auth
def random():
    game = get_random_game()
    return render_template('index.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], gamemaster = is_gamemaster(), games = [] if game is None else [game], players = get_players())

@app.route('/submissions')
@auth.oidc_auth
def submissions():
    gamemaster = is_gamemaster()
    return render_template('submissions.html', bucket = environ['GAME_NIGHT_S3_BUCKET'], gamemaster = gamemaster, games = get_submissions(gamemaster))