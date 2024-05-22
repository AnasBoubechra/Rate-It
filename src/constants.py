CHOICES = {
    'personal-development': 'Personal Development',
    'arts-and-humanities': 'Arts and Humanities',
    'language-learning': 'Language Learning',
    'computer-science': 'Computer Science',
    'social-sciences': 'Social Sciences',
    'math-and-logic': 'Math and Logic',
    'entertainment': 'Entertainment',
    'data-science': 'Data Science',
    'business': 'Business',
    'health': 'Health',
    'it': 'IT'
}

REASONS = {
    'inappropriate_content': 'Inappropriate Content',
    'bad_language': 'Bad Language',
    'spam': 'Spam',
    'other': 'Other'
}

REPORT_DESCRIPTION_LEN_MIN = 5
REPORT_DESCRIPTION_LEN_MAX = 100

MAX_POSTS_PER_DECK = 500
MAX_DECKS_PER_USER = 10

PER_PAGE_POST = 100
PER_PAGE_DECK = 6
# diffrent than deck DECK_FIELDS_LEN_.* / 14 letters then just add .. instead
# of showing the whole string (deck name)
DECK_TITLE_LENGTH = 14

# max username len & email activation key
STRING_LEN = 64

EMAIL_STRING_LEN = 100

URL_LEN_MAX = 500

QUERY_LEN_MAX = 30

NAME_LEN_MIN = 4
NAME_LEN_MAX = 25

PASSWORD_LEN_MIN = 6
PASSWORD_LEN_MAX = 35

POST_TITLE_LEN_MIN = 4
POST_TITLE_LEN_MAX = 30

POST_DESCRIPTION_LEN_MIN = 4
POST_DESCRIPTION_LEN_MAX = 100

DECK_TITLE_LEN_MIN = 4
DECK_TITLE_LEN_MAX = 45

DECK_DESCRIPTION_LEN_MIN = 0
DECK_DESCRIPTION_LEN_MAX = 65

DECK_FIELDS_LEN_MAX = 500

DECK_FIELDS_WORD_LEN_MAX = 20
