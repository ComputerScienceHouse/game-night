from flask import session
from wtforms.validators import DataRequired, Regexp, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, StringField
from urllib.request import urlopen

def _validate_expansion(form, field):
    from stuff.database import game_exists
    if field.data and not game_exists(field.data):
        raise ValidationError(f'"{field.data}" is not an expansion')

def _validate_link(form, field):
    try:
        urlopen(field.data)
    except:
        raise ValidationError('URL is unreachable')

def _validate_name(form, field):
    from stuff.database import game_exists
    if game_exists(field.data):
        raise ValidationError(f'"{field.data}" already exists')

def _validate_owner(form, field):
    from stuff.database import is_quartermaster
    if not is_quartermaster(session['userinfo']['preferred_username']) and field.data not in ['CSH', session['userinfo']['preferred_username']]:
        raise ValidationError('Only quartermasters can enter any owner')

class Game(FlaskForm):

    expansion = StringField('expansion', validators = [_validate_expansion])
    image = FileField('image', validators = [
        FileRequired(), FileAllowed(['jpg'])
    ])
    link = StringField('link')
    max_players = IntegerField('max_players', validators = [DataRequired()])
    min_players = IntegerField('min_players', validators = [DataRequired()])
    name = StringField('name', validators = [DataRequired(), _validate_name])
    owner = StringField('owner', validators = [DataRequired(), _validate_owner])

    def __init__(self, submitter = None):
        if submitter:
            super().__init__(
                expansion = '', link = '', max_players = 1, min_players = 1,
                name = '', owner = submitter
            )
        else:
            super().__init__()

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.max_players.data < self.min_players.data:
            self.max_players.errors.append('Max players < min players')
            return False
        return True
