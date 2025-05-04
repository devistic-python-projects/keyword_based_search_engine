from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    files = FileField('Upload Documents', validators=[DataRequired()], render_kw={'multiple': True})
    submit = SubmitField('Upload')