from .extensions import db
from flask import current_app, abort
from sqlalchemy import func
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from .constants import DECK_TITLE_LENGTH as dtl
from .users import User, AdminRequired
from .utils import (
    get_user_id,
    format_to_url,
)

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    deck_name = db.Column(db.String(100), nullable=False)
    deck_description = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(100), nullable=False)
    public = db.Column(db.Boolean, default=True)
    likes = db.Column(db.Integer, default=0)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime)
    fields = db.Column(db.String(100), nullable=False)
    posts = db.relationship('Post', backref='deck', cascade='all, delete', lazy=True)

    def __str__(self):
        _str = '%s. %s' % (self.id, self.deck_name)
        return str(_str)

    def fields_choices(self):
        return [(word, word) for word in self.fields.split()]

    def fields_list(self):
        return list(self.fields)

    def formatted_deck_name(self):
        return format_to_url(self.deck_name.lower())

    def truncate_deck_name(self):
        return self.deck_name[:dtl] + '..' if len(self.deck_name) > dtl else self.deck_name

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    field = db.Column(db.String(20), nullable=False)
    votes = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    url = db.Column(db.String(200))

    def number_of_posts(self):
        return len(self.posts)

    @staticmethod
    def get_unique_field_per_page(deck_id):
        # Perform the paginated query to get posts for the specified deck_id and page
        posts = Post.query.filter_by(deck_id=deck_id).order_by(Post.field, Post.votes.desc())

        # Extract unique values of the 'field' column from the posts on the current page
        unique_field_per_page = db.session.query(func.distinct(Post.field)).filter(Post.deck_id == deck_id, Post.id.in_([post.id for post in posts])).all()

        # Convert the result to a list of values
        unique_field_values = [value[0] for value in unique_field_per_page]

        return unique_field_values, posts

def if_authorized(deck_id):
    if deck_id is None:
        abort(400)
    deck = Deck.query.get(deck_id)
    if deck is None:
        abort(404)
    if not deck.public and deck.user_id != get_user_id():
        abort(403)
    return deck

def update_deck_last_modified(deck):
    if deck:
        deck.last_modified = datetime.utcnow()

class PostView(AdminRequired, ModelView):
    column_searchable_list = ('user_id', User.id)
    column_filters = ('title', 'deck_id',
                      'url', 'field', 'description', 'votes')

    def __init__(self, session):
        super(PostView, self).__init__(Post, session)

class DeckView(AdminRequired, ModelView):
    column_searchable_list = ('user_id', User.id)
    column_filters = ('deck_name', 'user_id',
                      'deck_description', 'creation_date')

    def __init__(self, session):
        super(DeckView, self).__init__(Deck, session)
