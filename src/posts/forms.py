from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField, SubmitField,
                     BooleanField, TextAreaField, IntegerField)
from wtforms.validators import ValidationError, DataRequired, URL, Length, Regexp, Optional
from ..models import Post, Deck
from ..constants import CHOICES, REASONS
import re
from ..constants import (
    URL_LEN_MAX,
    POST_TITLE_LEN_MIN,
    POST_TITLE_LEN_MAX,
    POST_DESCRIPTION_LEN_MIN,
    POST_DESCRIPTION_LEN_MAX,
    DECK_FIELDS_LEN_MAX,
    DECK_TITLE_LEN_MIN,
    DECK_TITLE_LEN_MAX,
    DECK_DESCRIPTION_LEN_MIN,
    DECK_DESCRIPTION_LEN_MAX,
    REPORT_DESCRIPTION_LEN_MIN,
    REPORT_DESCRIPTION_LEN_MAX
)

error_msg = f"This field can only contain letters and numbers"

class PostForm(FlaskForm):
    title = StringField('Title',
                        validators=[DataRequired(), Length(min=POST_TITLE_LEN_MIN,
                                                           max=POST_TITLE_LEN_MAX),
                                    Regexp(r'^[ \w\d]+$',0,error_msg)])
    description = TextAreaField('Description',
                              validators=[DataRequired(), Length(min=POST_DESCRIPTION_LEN_MIN,
                                                                 max=POST_DESCRIPTION_LEN_MAX),
                                          Regexp(r'^[ \w\d]+$',0,error_msg)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(max=URL_LEN_MAX)])
    field = SelectField('field',choices=[], validate_choice=True)
    submit = SubmitField('Add')


class DeckForm(FlaskForm):
    deck_name = StringField('Deck Title',
                        validators=[DataRequired(), Length(min=DECK_TITLE_LEN_MIN,max=DECK_TITLE_LEN_MAX),
                                    Regexp(r'^[ \w\d]+$',0,error_msg)])
    deck_description = TextAreaField('Deck description',
                                   validators=[Length(min=DECK_DESCRIPTION_LEN_MIN,max=DECK_DESCRIPTION_LEN_MAX),
                                               Regexp(r'^[ \w\d]*$',0,error_msg)])
    category = SelectField('Categories', choices=CHOICES.keys())
    fields = TextAreaField('Table Fields', validators=[DataRequired(), Length(max=DECK_FIELDS_LEN_MAX),
                                                       Regexp(r'^[ \w\d]+$',0,error_msg)])
    public = BooleanField('Public')
    submit = SubmitField('Create Deck')

    def validate_fields(self, field):
        long_fields = [i for i in field.data.split() if len(i) >= 20]
        if long_fields:
            error_msg = f"Each field can have only up to 15 characters"
            raise ValidationError(error_msg)

class ReportForm(FlaskForm):
    reason = SelectField('Reason', choices=REASONS.values())
    deck_id = IntegerField([Optional()])
    description = TextAreaField('Description',
                              validators=[DataRequired(), Length(min=REPORT_DESCRIPTION_LEN_MIN,
                                                                 max=REPORT_DESCRIPTION_LEN_MAX),
                                          Regexp(r'^[ \w\d]+$',0,error_msg)])

class VoteForm(FlaskForm):
    post_id = IntegerField('Post ID')
    vote_type = IntegerField('Vote Type', validators=[DataRequired()])

class UrlForm(FlaskForm):
    url = StringField('URL',
                      validators=[DataRequired(), URL(), Length(max=URL_LEN_MAX)])

class LikeForm(FlaskForm):
    like_id = IntegerField('Like id')
