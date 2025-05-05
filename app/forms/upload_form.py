from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField

class UploadForm(FlaskForm):
    files = FileField('Upload Documents', render_kw={"multiple": True})
    submit = SubmitField('Upload')
