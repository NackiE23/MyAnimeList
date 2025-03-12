from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, DateField, FileField, SelectField, MultipleFileField
from wtforms.validators import DataRequired

from site_package.models.media import MediaTypeEnum


class CategoryForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    description = TextAreaField(label="Description")
    submit = SubmitField()


class MediaForm(FlaskForm):
    type = SelectField(label="Media Type", coerce=str)
    name = StringField(label="Name", validators=[DataRequired()])
    alternative_name = StringField(label="Alternative name")
    description = TextAreaField(label="Description")
    grade = IntegerField(label="Grade")
    release = DateField(label="Release", validators=[DataRequired()])
    img = FileField(label="Image")
    submit = SubmitField(label="Save")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type.choices = [(t.value, t.name) for t in MediaTypeEnum]


class MediaImageForm(FlaskForm):
    imgs = MultipleFileField(label="Images")
    description = StringField(label="Description")
    order = IntegerField(label="Order")
    submit = SubmitField(label="Save")
