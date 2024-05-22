from flask import Flask, request, render_template, has_request_context

from werkzeug.exceptions import HTTPException

from .extensions import db, csrf, htmx, mail, login_manager, admin

from .utils import (pretty_date, get_random_urlsafe_string,
                    check_none_values)
from .config import config

from .users.routes import users
from .posts import posts
from .main import main

__all__ = ['create_app']

BLUEPRINTS = (
    posts,
    main,
    users
)

def create_app(config_name=None):

    blueprints = BLUEPRINTS

    app = Flask(__name__, instance_relative_config=True)

    configure_app(app, config_name)
    configure_extensions(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    configure_blueprints(app, blueprints)

    return app

def configure_app(app, config_name=None):

    config_name = config_name or 'default'

    # A function that checks if there is an empty value in the config
    check_none_values(config[config_name])

    app.config.from_object(config[config_name])

    if hasattr(config[config_name], 'init_app'):
        config[config_name].init_app(app)

    print('=' * 10, f"> Running in {config_name} mode!\n")

def configure_template_filters(app):
    """
    A little cleanup after jinja template rendering
    : removing spaces, and striping new lines
    """
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    strip_trailing_newlines = True

    @app.template_filter()
    def _pretty_date(value):
        return pretty_date(value)
    @app.template_filter()
    def format_date(value, format='%Y-%m-%d'):
        return value.strftime(format)

def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

def configure_extensions(app):
    db.init_app(app)
    csrf.init_app(app)
    htmx.init_app(app)
    mail.init_app(app)
    admin.init_app(app)
    login_manager.init_app(app)

def configure_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_error(error):
        if not isinstance(error, HTTPException):
            if not app.debug:
                return render_template('errors/500.html'), 500
            raise
        return render_template('errors/errors.html', error=error), error.code
    @app.errorhandler(404)
    def custom_error_404(error):
        return render_template('errors/404.html', error=error), error.code
