from flask import session
from wtforms.validators import DataRequired, Regexp, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, StringField
from urllib.request import urlopen

def _owner_limit(form, field):
    from game_night.database import is_gamemaster
    if not is_gamemaster() and field.data not in ('CSH', session['userinfo']['preferred_username']):
        raise ValidationError('Only gamemasters can enter any owner')

def _unique(form, field):
    from game_night.database import game_exists
    if game_exists(field.data):
        raise ValidationError(f'"{field.data}" already exists')

def _url_reachable(form, field):
    try:
        urlopen(field.data)
    except:
        raise ValidationError('URL is unreachable')

class Game(FlaskForm):

    image = FileField('image', validators = [FileRequired(), FileAllowed(['jpg'])])
    link = StringField('link', validators = [DataRequired(), Regexp('https://boardgamegeek.com/.*'), _url_reachable])
    max_players = IntegerField('max_players', validators = [DataRequired()])
    min_players = IntegerField('min_players', validators = [DataRequired()])
    name = StringField('name', validators = [DataRequired(), _unique])
    owner = StringField('owner', validators = [DataRequired(), _owner_limit])

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.max_players.data < self.min_players.data:
            self.max_players.errors.append('Max players < min players')
            return False
        return True