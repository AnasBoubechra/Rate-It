from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_admin.menu import MenuLink
from flask import redirect, url_for
from flask_mailman import Mail
from flask_htmx import HTMX

login_manager = LoginManager()
csrf = CSRFProtect()
db = SQLAlchemy()
htmx = HTMX()
mail = Mail()

login_manager.login_view = 'users.login'
login_manager.login_message_category = 'notice'

login_manager.refresh_view = "users.login"
login_manager.needs_refresh_message = (
    "To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "notice"

class HomeView(AdminIndexView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("main.home"))

admin = Admin(name='Rate it Admin', template_mode='bootstrap3', index_view=HomeView(name='Home', url="/admin"))
admin.add_link(MenuLink(name='Back to main', url='/', icon_type='glyph', icon_value='glyphicon-circle-arrow-left'))
admin.add_link(MenuLink(name='Logout', url='/logout', icon_type='glyph', icon_value='glyphicon-log-out'))

from .users import UserView
from .models import PostView, DeckView
from .main import ContactUsView

admin.add_view(ContactUsView(db.session))
admin.add_view(UserView(db.session))
admin.add_view(PostView(db.session))
admin.add_view(DeckView(db.session))
