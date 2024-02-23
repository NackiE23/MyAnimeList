from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateField, FileField, PasswordField, SubmitField
from wtforms.validators import Length, DataRequired, EqualTo, ValidationError, Email

from site_package.models.user import User


class AnimeModelForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    alternative_name = StringField(label="Alternative name")
    description = TextAreaField(label="Description")
    grade = IntegerField(label="Grade")
    release = DateField(label="Release", validators=[DataRequired()])
    img = FileField(label="Image")
    submit = SubmitField(label="Create an anime info")
