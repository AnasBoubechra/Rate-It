import os
from datetime import timedelta

BASEDIR = os.path.dirname(os.path.dirname(__file__)) + "/instances"

def create_sqlite_uri(db_name):
    return "sqlite:///" + os.path.join(BASEDIR, db_name)

__all__ = ['config']

class Config:
    SECRET_KEY =os.environ.get('SECRET_KEY')

    TURNSTILE_SECRET_KEY=os.environ.get('TURNSTILE_SECRET_KEY')
    TURNSTILE_SITE_KEY=os.environ.get('TURNSTILE_SITE_KEY')
    CF_API_TOKEN =os.environ.get('CF_API_TOKEN')
    CF_URL=os.environ.get('CF_URL')

    PROJECT_NAME =os.environ.get('PROJECT_NAME')

    NONCE_LENGTH = 16
    TOKEN_MAX_AGE_SECONDS = 3600

    FLASK_ADMIN_SWATCH = "cerulean"

    REMEMBER_COOKIE_SAMESITE = "Strict"
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

    MAIL_BACKEND = "smtp"
    MAIL_SERVER=os.environ.get('MAIL_SERVER')
    MAIL_PORT=os.environ.get('MAIL_PORT')
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX =os.environ.get('MAIL_SUBJECT_PREFIX')
    MAIL_DEFAULT_RECIPIENT=os.environ.get('MAIL_DEFAULT_RECIPIENT')
    MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER')

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = create_sqlite_uri("db/production.db")

    @classmethod
    def init_app(cls, app):
        import logging
        from logging.handlers import SMTPHandler

        class RequestFormatter(logging.Formatter):
            def format(self, record):
                if has_request_context():
                    record.url = request.url
                    record.remote_addr = request.remote_addr
                    record.user_agent = request.user_agent.string
                else:
                    record.url = None
                    record.remote_addr = None
                    record.user_agent = None
                return super().format(record)

        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_DEFAULT_SENDER,
            toaddrs=[cls.MAIL_DEFAULT_RECIPIENT],
            subject=cls.MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=(cls.MAIL_USERNAME, cls.MAIL_PASSWORD),
            secure=())

        mail_handler.setLevel(logging.ERROR)
        if not app.debug:
            app.logger.addHandler(mail_handler)

class DevelopmentConfig(Config):
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXPLAIN_TEMPLATE_LOADING = False
    SQLALCHEMY_ECHO = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = create_sqlite_uri("db/development.db")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = create_sqlite_uri("db/testing.db")

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
