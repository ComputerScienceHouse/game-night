from flask import abort, Flask, jsonify, redirect, render_template
from os import environ
from flaskext.markdown import Markdown
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from game_night.database import *

app = Flask(__name__)
app.config['PREFERRED_URL_SCHEME'] = environ.get('URL_SCHEME', 'https')
app.config['SECRET_KEY'] = environ['SECRET_KEY']
app.config['SERVER_NAME'] = environ['SERVER_NAME']
app.config['WTF_CSRF_ENABLED'] = False
app.jinja_env.lstrip_blocks = True
app.jinja_env.trim_blocks = True
app.url_map.strict_slashes = False

Markdown(app)

_client_info = {
    'client_id': environ['OIDC_CLIENT_ID'],
    'client_secret': environ['OIDC_CLIENT_SECRET']
}
_auth = OIDCAuthentication(app, client_registration_info = _client_info, issuer = environ['OIDC_ISSUER'])

@app.route('/api')
@require_read_key
def api():
    return jsonify(list(get_games()))

@app.route('/api/count')
@require_read_key
def api_count():
    return jsonify(get_count())

@app.route('/api/key', methods = ['GET', 'POST'])
@app.route('/api/key/write', defaults = {'write': True}, methods = ['GET', 'POST'])
@require_gamemaster
def api_key(write = False):
    return jsonify(generate_api_key(write))

@app.route('/api/newest')
@require_read_key
def api_newest():
    return jsonify(list(get_newest_games()))

@app.route('/api/owners')
@require_read_key
def api_owners():
    return jsonify(get_owners())

@app.route('/api/random')
@app.route('/api/random/<int:sample_size>')
@require_read_key
def api_random(sample_size = 1):
    sample = list(get_random_games(sample_size))
    return jsonify(sample[0] if len(sample) == 1 else sample)

@app.route('/delete/<game_name>', methods = ['GET', 'POST'])
@_auth.oidc_auth
@require_gamemaster
def delete(game_name):
    if delete_game(game_name):
        return redirect('/')
    abort(404)

@app.route('/')
@_auth.oidc_auth
def index():
    return render_template('index.html', bucket = environ['S3_BUCKET'], gamemaster = is_gamemaster(), games = get_games(), owners = get_owners(True), players = get_players())

@app.route('/random')
@_auth.oidc_auth
def random():
    return render_template('index.html', bucket = environ['S3_BUCKET'], gamemaster = is_gamemaster(), games = get_random_games(1), owners = get_owners(True), players = get_players())

@app.route('/rules/<game_name>')
@_auth.oidc_auth
def rules(game_name):
    game = get_game(game_name)
    if game is None:
        abort(404)
    return render_template('rules.html', bucket = environ['S3_BUCKET'], game = game, gamemaster = is_gamemaster(), owners = get_owners(True), players = get_players())

@app.route('/submissions')
@_auth.oidc_auth
def submissions():
    return render_template('index.html', bucket = environ['S3_BUCKET'], gamemaster = is_gamemaster(), games = get_submissions(), owners = get_owners(True), players = get_players())

@app.route('/submit', methods = ['GET', 'POST'])
@_auth.oidc_auth
def submit():
    if request.method == 'GET':
        return render_template('submit.html', form = Game(link = '', max_players = 1, min_players = 1, name = '', owner = session['userinfo']['preferred_username']), gamemaster = is_gamemaster(), owners = get_owners(True), players = get_players())
    tup = submit_game()
    return render_template('submit.html', form = tup[0], error = tup[1], gamemaster = is_gamemaster(), owners = get_owners(True), players = get_players()) if isinstance(tup, tuple) else redirect('/')