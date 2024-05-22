from flask import request, redirect, url_for
from ..extensions import db, login_manager
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..utils import get_current_time
from flask_admin.contrib import sqla
from ..constants import STRING_LEN, PASSWORD_LEN_MAX , EMAIL_STRING_LEN
from .constants import USER, USER_ROLE, ADMIN, INACTIVE, USER_STATUS

import hashlib

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(STRING_LEN))
    email = db.Column(db.String(EMAIL_STRING_LEN), unique=True)
    real_email_hash = db.Column(db.Boolean, default=False)
    email_activation_key = db.Column(db.String(STRING_LEN))
    created_time = db.Column(db.DateTime, default=get_current_time)
    _password = db.Column('password', db.String(PASSWORD_LEN_MAX), nullable=False)
    decks = db.relationship('Deck', backref='user', cascade='all, delete', lazy=True)

    def __str__(self):
        _str = '%s. %s' % (self.id, self.username)
        return str(_str)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = generate_password_hash(password)

    # Hide password encryption by exposing password field only.
    password = db.synonym('_password',
                          descriptor=property(_get_password,
                                              _set_password))
    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    role_code = db.Column(db.SmallInteger, default=USER, nullable=False)


    @property
    def role(self):
        return USER_ROLE[self.role_code]

    def is_admin(self):
        return self.role_code == ADMIN

    def is_authenticated(self):
        return True

    # One-to-many relationship between users and user_statuses.
    status_code = db.Column(db.SmallInteger, default=INACTIVE)

    @property
    def status(self):
        return USER_STATUS[self.status_code]

    @classmethod
    def authenticate(cls, login, password):
        user = cls.query.filter(User.email.ilike(login)).first()

        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False

        return user, authenticated

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

    def check_email(self, email):
        return User.query.filter(User.email == email).count() == 0

    def check_username(self, username):
        return User.query.filter(User.username == username).count() == 0


    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://www.gravatar.com/avatar'

        if self.real_email_hash:
            hash = hashlib.md5((self.email).encode('utf-8')).hexdigest()
        else:
            hash = hashlib.md5((str(self.created_time)).encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'\
            .format(url=url, hash=hash, size=size, default=default, rating=rating)

class AdminRequired():
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("main.home"))

class UserView(AdminRequired, sqla.ModelView):
    column_list = ('id', 'username', 'email', 'role_code', 'status_code',
                   'created_time', 'decks')
    column_sortable_list = ('id', 'username', 'email', 'created_time',
                            'role_code', 'status_code')
    column_searchable_list = ('email', User.email)
    column_searchable_list = ('email', User.username)
    column_filters = ('id', 'username', 'email', 'created_time', 'role_code')

    form_excluded_columns = ('password')

    form_choices = {
        'role_code': [
            ('2', 'User'),
            ('0', 'Admin')
        ],
        'status_code': [
            ('0', 'Inactive Account'),
            ('1', 'New Account'),
            ('2', 'Active Account')
        ]
    }

    column_choices = {
        'role_code': [
            (2, 'User'),
            (1, 'Staff'),
            (0, 'Admin')
        ],
        'status_code': [
            (0, 'Inactive Account'),
            (1, 'New Account'),
            (2, 'Active Account')
        ]
    }

    def __init__(self, session):
        super(UserView, self).__init__(User, session)
