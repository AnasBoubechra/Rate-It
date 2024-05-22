from flask import current_app, request
from flask_login import current_user
from threading import Thread
from hashlib import md5
from uuid import uuid4
import urllib.parse
import requests
import datetime
import secrets
import re

from .constants import (
    DECK_FIELDS_WORD_LEN_MAX,
    DECK_FIELDS_LEN_MAX,
)

ALLOWED_PATTERN = re.compile(r'^[ \w\d]+$')

def turnstile_verify():
    VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    data = {
        "secret": current_app.config['TURNSTILE_SECRET_KEY'],
        "response": request.form.get('cf-turnstile-response'),
    }
    r = requests.post(VERIFY_URL, data=data)
    return r.json()["success"] if r.status_code == 200 else False

def check_none_values(Config):
    missing_configs = [attr_name for attr_name in dir(Config) \
                       if not attr_name.startswith('__') and getattr(Config, attr_name) is None]
    if missing_configs:
        error_msg = f"The following configuration values are missing: {', '.join(missing_configs)}"
        raise ValueError(error_msg)

def get_random_urlsafe_string(length):
    return secrets.token_urlsafe(length)[:length]

def get_uuid():
    return str(uuid4())

def format_hash_ip(ip):
    return md5(ip.encode('utf-8').split(b',')[0].strip()).hexdigest()

def format_to_url(string):
    return string.replace(' ', '-') if ' ' in string else urllib.parse.quote(string, safe='~')

# simple function to remove extra spaces from strings
def rs(string):
    return ' '.join(string.split())

def get_user_id():
    return current_user.id if current_user.is_authenticated else 1000

def get_current_time():
    return datetime.datetime.utcnow()

def format_date(value, format='%Y-%m-%d'):
    return value.strftime(format)

def pretty_date(dt, default=None):
    # Returns string representing "time since" eg 3 days ago, 5 hours ago etc.
    if default is None:
        default = 'just now'

    if dt is None:
        return default

    now = datetime.datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, 'year', 'years'),
        (diff.days / 30, 'month', 'months'),
        (diff.days / 7, 'week', 'weeks'),
        (diff.days, 'day', 'days'),
        (diff.seconds / 3600, 'hour', 'hours'),
        (diff.seconds / 60, 'minute', 'minutes'),
        (diff.seconds, 'second', 'seconds'),
    )

    for period, singular, plural in periods:

        if not period:
            continue

        if int(period) >= 1:
            if int(period) > 1:
                return u'%d %s ago' % (period, plural)
            return u'%d %s ago' % (period, singular)

    return default

def validate_user_input(input_value, max_length=None):
    if not ALLOWED_PATTERN.match(input_value):
        raise ValueError("Input Error: Only letters and numbers are allowed!")

    if max_length is not None and len(input_value) > max_length:
        raise ValueError(f"Input Error: the string length can only be {max_length}")

def validate_table_fields(input_value):
    if not ALLOWED_PATTERN.match(input_value):
        raise ValueError("Input Error: Only letters and numbers are allowed!")

    words = input_value.split()
    if len(words) > DECK_FIELDS_LEN_MAX:
        raise ValueError(f"Oops... The table name '{input_value}' can only be between \
                         {DECK_FIELDS_LEN_MIN} and {DECK_FIELDS_LEN_MAX} words.")

    if any(len(word) > DECK_FIELDS_WORD_LEN_MAX for word in words):
        raise ValueError(f"Oops... Each word in the table name can be up to {DECK_FIELDS_WORD_LEN_MAX} characters.")
