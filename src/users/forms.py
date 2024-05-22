from flask_wtf import FlaskForm

from flask_login import current_user

from wtforms import (ValidationError, HiddenField, BooleanField, StringField,
                     PasswordField, SubmitField, TextAreaField)

from wtforms.validators import (InputRequired, Length, Email,
                                EqualTo, ValidationError,
                                Regexp, UUID)

from ..constants import (NAME_LEN_MIN, NAME_LEN_MAX, PASSWORD_LEN_MIN,
                     PASSWORD_LEN_MAX)

from .models import User

error_msg = """<u><b>The password should contain:</b></u>
<br>
* At least one <b><u>special character</u></b> for example <code># ? ! @ $ % ^</code><br>
* At least one <b><u>letter</u></b>.<br>
* At least one <b><u>number</u></b>.<br>
"""

terms_html = '<a target="blank" href="/terms">Terms of Service</a>'

class LoginForm(FlaskForm):
    next = HiddenField()
    email = StringField('Email', [InputRequired(), Email()])
    password = PasswordField('Password', [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SingupForm(FlaskForm):
    username = StringField('Name', [InputRequired(), Length(NAME_LEN_MIN, NAME_LEN_MAX),
                                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                           'Usernames must have only letters, ' 'numbers, dots or underscores') ])
    email = StringField('Email', [InputRequired(), Email()])
    password = PasswordField('Password',
                             [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX),
                              Regexp(r'^(?!^(.{0,7}|[^0-9]*|[^a-z]*|[a-zA-Z0-9]*)$)',0,error_msg)],
                             description=f" {PASSWORD_LEN_MAX} or more characters.")
    confirm_password = PasswordField('Confirm Password', [InputRequired(),
                                                          EqualTo('password'),
                                                          Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])

    submit = SubmitField('Sign up')

    def validate_username(self, username):
        if not User.check_username(self, username.data):
            raise ValidationError('This username is taken!')

    def validate_email(self, email):
        if not User.check_email(self, email.data):
            raise ValidationError('This email is taken')

class UpdateSettingsForm(FlaskForm):
    username = StringField('Name', [InputRequired(), Length(NAME_LEN_MIN, NAME_LEN_MAX),
                                    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                           'Usernames must have only letters, numbers, dots or underscores') ])
    email = StringField('Email', [InputRequired(), Email()])

    submit = SubmitField('Save')

    def validate_username(self, username):
        if current_user.username != username.data and not current_user.check_username(username.data):
            raise ValidationError('This username already exits!, please pick another one.', 'error')
    def validate_email(self, email):
        if current_user.email != email.data and not current_user.check_email(email.data):
            raise ValidationError('This email already exists!', 'error')

class ChangePasswordForm(FlaskForm):
    email_activation_key = HiddenField([UUID()])
    email = HiddenField('email',[Email()])
    password = PasswordField('Password',
                             [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX),
                              Regexp(r'^(?!^(.{0,7}|[^0-9]*|[^a-z]*|[a-zA-Z0-9]*)$)',0,error_msg)],
                             description=f" {PASSWORD_LEN_MAX} or more characters.")
    confirm_password = PasswordField('Confirm Password', [InputRequired(),
                                                          EqualTo('password'),
                                                          Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    submit = SubmitField('Change password')

# change the password from the settings and not by sending a reset_link
class UserChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current password', [InputRequired()])
    password = PasswordField('Password',
                             [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX),
                              Regexp(r'^(?!^(.{0,7}|[^0-9]*|[^a-z]*|[a-zA-Z0-9]*)$)',0,error_msg)],
                             description=f" {PASSWORD_LEN_MAX} or more characters.")
    confirm_password = PasswordField('Confirm Password', [InputRequired(),
                                                          EqualTo('password'),
                                                          Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    submit = SubmitField('Change password')

    def validate_current_password(self, password):
        if not current_user.check_password(password.data):
            raise ValidationError("Incorrect password")

class RecoverPasswordForm(FlaskForm):
    email = StringField('Your email', [Email()])
    submit = SubmitField('Send instructions')
