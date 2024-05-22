from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, EmailField)
from wtforms.validators import InputRequired, Length, Email

class ContactUsForm(FlaskForm):
    name = StringField('Name', [InputRequired(), Length(max=64)])
    email = EmailField('Your Email', [InputRequired(), Email(), Length(max=64)])
    subject = StringField('Subject', [InputRequired(), Length(5, 128)])
    message = TextAreaField('Your Message', [InputRequired(), Length(10, 1024)])
    submit = SubmitField('Submit')
