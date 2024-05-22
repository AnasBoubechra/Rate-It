from functools import wraps

from flask import abort, flash, redirect, url_for, request, render_template

from flask_htmx import make_response as htmx_make_response

from flask_login import current_user, login_fresh

from .modules.http import url_has_allowed_host_and_scheme

from .extensions import login_manager, htmx

from .utils import get_user_id

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def requires_fresh_session(f):
    @wraps(f)
    def decorated_route(*args, **kwargs):
        if current_user.is_authenticated and not login_fresh():
            referrer = request.referrer if \
                url_has_allowed_host_and_scheme(request.referrer, request.host) else '/'
            flash(
                login_manager.needs_refresh_message ,
                login_manager.needs_refresh_message_category
            )
            if htmx:
                return htmx_make_response(location=url_for(login_manager.refresh_view, next=referrer))
            return redirect(url_for(login_manager.refresh_view, next=referrer))
        return f(*args, **kwargs)
    return decorated_route
