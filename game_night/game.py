from wtforms.validators import DataRequired, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, StringField

def _unique(form, field):
    from game_night.database import game_exists
    if game_exists(field.data):
        raise ValidationError(f'"{field.data}" already exists')

class Game(FlaskForm):

    image = FileField('image', validators = [FileRequired(), FileAllowed(['jpg'])])
    link = StringField('link', validators = [DataRequired()])
    max_players = IntegerField('max_players', validators = [DataRequired()])
    min_players = IntegerField('min_players', validators = [DataRequired()])
    name = StringField('name', validators = [DataRequired(), _unique])
    owner = StringField('owner', validators = [DataRequired()])

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.max_players.data < self.min_players.data:
            self.max_players.errors.append('Max players < min players')
            return False
        return True