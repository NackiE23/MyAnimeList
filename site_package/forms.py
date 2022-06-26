from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, DateField, FileField
from wtforms.validators import Length, DataRequired


class AddAnimeForm(FlaskForm):
    def validate_name(self):
        pass

    name = StringField(label="Name", validators=[Length(60), DataRequired()])
    alternative_name = StringField(label="Alternative name", validators=[Length(60)])
    description = TextAreaField(label="Description")
    grade = IntegerField(label="Grade")
    release = DateField(label="Release", validators=[DataRequired()])
    img = FileField(label="Image")
