from flask import (render_template, url_for, flash, Response, current_app,
                   abort, redirect, request, Blueprint)

from flask_login import (login_required, login_user, current_user,
                         logout_user, login_fresh, user_logged_in,
                         user_login_confirmed)

from flask_htmx import make_response as htmx_make_response

from .forms import (SingupForm, LoginForm,
                    RecoverPasswordForm,
                    ChangePasswordForm,
                    UpdateSettingsForm,
                    UserChangePasswordForm)

from .utils import (get_data_from_hash, generate_hash,
                    confirm_user_mail, send_email)

from . import User, ACTIVE

from ..utils import rs, get_uuid

from ..modules.http import url_has_allowed_host_and_scheme

from ..decorators import requires_fresh_session

from ..extensions import db, htmx, login_manager

from ..models import Deck

users = Blueprint('users', __name__)

@users.route("/account")
@login_required
def account():
    likes = sum([deck.likes for deck in current_user.decks])
    s = request.args.get('s')
    if not s:
        return render_template("user/user.html" ,likes=likes)

    template_mapping = {
        'profile': 'user/profile.html',
        'settings': 'user/settings.html',
        'danger_zone': 'user/danger_zone.html'
    }

    template = template_mapping.get(s)

    if template and htmx:
        return render_template(template, likes=likes)
    abort(400)

@users.route("/user/gravatar", methods=['PUT'])
@login_required
def user_gravatar():
    real_email_hash = True if request.form.get('reh') else False
    if real_email_hash != current_user.real_email_hash:
        current_user.real_email_hash = real_email_hash
        db.session.add(current_user)
        db.session.commit()
        flash("Avatar settings changed", "success")
        return htmx_make_response(location=url_for('users.account'))
    abort(400)

@users.route('/delete/account', methods=['DELETE'])
@login_required
@requires_fresh_session
def delete_account():
    try:
        db.session.delete(current_user)
        db.session.commit()
        flash("Your account was successfully deleted", "success")
        logout_user()
        return htmx_make_response(refresh=True)
    except:
        abort(400)

@users.route('/delete/decks', methods=["DELETE"])
@login_required
@requires_fresh_session
def delete_decks():
    decks = Deck.query.filter_by(user_id=current_user.id)
    if decks.count() != 0:
        decks.delete()
        db.session.commit()
        flash("All the decks were deleted", "success")
        return htmx_make_response(location=url_for('posts.decks'))

    flash("You don't have any deck yet!", "error")
    return htmx_make_response(location=url_for('posts.decks'))

@users.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = SingupForm()

    if form.validate_on_submit():
        user = User()
        user.status_code = 1
        user.account_type = 0
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()

        confirm_user_mail(form.username.data, form.email.data, 'Confirm your account for ',
                          'email_templates/html/_confirm_account.html',
                          'email_templates/txt/_confirm_account.txt')

        flash('Confirmation email sent to ' + form.email.data + ' Please verify!', 'success')
        if htmx:
            return htmx_make_response(redirect=url_for('users.login'))
        return redirect(url_for('users.login'))

    if htmx:
        return render_template("partials/user/signup.html", form=form, _active_signup=True,
                               SITE_KEY=current_app.config['TURNSTILE_SITE_KEY'])
    return render_template('user/signup.html', form=form, _active_signup=True,
                           SITE_KEY=current_app.config['TURNSTILE_SITE_KEY'])


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and login_fresh():
        flash("You are already logged in!", "notice")
        return redirect(url_for('main.home'))

    next=request.args.get('next', url_for('posts.decks'))

    if not url_has_allowed_host_and_scheme(next, request.host):
        return abort(400)

    form = LoginForm(login=request.args.get('login', None), next=next)

    login_failed=False

    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.email.data, form.password.data)

        if user and authenticated:

            if user.status_code != 2:
                flash("Please verify your email address to continue", "error")
                return redirect(url_for('users.login'))

            remember = True if request.form.get('remember') else False

            if login_user(user, remember=remember):
                flash("Logged in", 'success')
            if htmx:
                return htmx_make_response(redirect=next)
            return redirect(next)
        else:
            login_failed=True
            flash('Invalid username or password', 'error')

    resp = {
        'form':form,
        'htmx': htmx,
        'login_failed': login_failed
    }

    if htmx:
        return render_template("partials/user/login.html", **resp)
    return render_template("user/login.html", **resp)

@users.route("/logout")
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('main.home'))
    logout_user()
    flash("Logged out!", "success")
    return redirect(url_for('main.home'))

@users.route('/confirm/account/<secretstring>', methods=['GET', 'POST'])
def confirm_account(secretstring):
    uname, uemail = get_data_from_hash(secretstring, salt="confirm_account")
    user = User.query.filter_by(username=uname).first_or_404()
    if user.email != uemail:
        # means the user already exists ... he only sent the request to change his email account ...
        user.email = uemail
        db.session.add(user)
        db.session.commit()
        flash("Your email was successfully changed", "success")
        return redirect(url_for('main.home'))
    user.status_code = ACTIVE
    db.session.add(user)
    db.session.commit()
    if user_login_confirmed:
        flash('Your account was confirmed succsessfully!!', 'success')
    else:
        flash('We failed to confirm your account :/', 'error')

    return redirect(url_for('users.login'))

@users.route('/reset/password', methods=['GET', 'POST'])
def reset_password():
    form = RecoverPasswordForm()

    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter(User.email.ilike(form.email.data)).first()

            if user:
                user.email_activation_key = get_uuid()
                db.session.add(user)
                db.session.commit()
                email = generate_hash(user.email, salt="reset_password")
                subject = 'Reset your password in ' + current_app.config['PROJECT_NAME']
                url = url_for('users.change_password', email=email,
                              email_activation_key=user.email_activation_key, _external=True)
                html = render_template('email_templates/html/_reset_password.html', project=current_app.config['PROJECT_NAME'],
                                       username=user.username, url=url)
                text = render_template('email_templates/txt/_reset_password.txt', project=current_app.config['PROJECT_NAME'],
                                       username=user.username, url=url)

                send_email(subject, html, text, user.email)
                flash('Please see your email for instructions on how to access your account', 'success')

                if htmx:
                    return htmx_make_response(redirect=url_for('users.login'))

                return redirect(url_for('users.login'))
            else:
                flash('Sorry, no user found for that email address', 'error')
        flash("Please provide a valid email address!", "error")
    if htmx:
        return htmx_make_response(redirect=url_for('users.login'))
    return render_template('user/reset_password.html', form=form)

@users.route('/change/password', methods=['GET', 'POST'])
@requires_fresh_session
def change_password():
    email = get_data_from_hash(request.args.get("email"), salt="change_password")
    form = ChangePasswordForm(email_activation_key=request.args.get('email_activation_key'), email=email)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, email_activation_key=form.email_activation_key.data).first()
        if user:
            user.password = form.password.data
            user.email_activation_key = None
            db.session.add(user)
            db.session.commit()
            flash("Your password has been changed, log in again", "success")
            return redirect(url_for("users.login"))
        flash("User not found :/", "error")
    return render_template("user/change_password.html", form=form)

@users.route("/change/password/settings", methods=['POST', 'GET'])
@login_required
def user_change_password():
    if not htmx:
        abort(400)
    form = UserChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.add(current_user)
        db.session.commit()
        flash("Your password was changed successfully", "success")
        return htmx_make_response(location=url_for('users.account'))
    return render_template("partials/user_change_password.html", form=form)

@users.route('/update/settings', methods=['GET', 'POST'])
@login_required
@requires_fresh_session
def update_settings():
    form = UpdateSettingsForm()
    if not htmx:
        abort(400)
    if request.method == "POST":
        if form.validate_on_submit():
            if form.email.data != current_user.email:
                confirm_user_mail(form.username.data, form.email.data,
                                          'Confirm your account for ',
                                          'email_templates/html/_confirm_email.html',
                                          'email_templates/txt/_confirm_email.txt')
                flash("A confirmation link was just sent to " + form.email.data + " Please verify it!", "notice")
            if form.username.data != current_user.username:
                current_user.username = rs(form.username.data)
                flash(f'Your username changed to {form.username.data}', 'success')
                db.session.add(current_user)
                db.session.commit()
            return htmx_make_response(location=url_for('users.account'))
    return render_template("partials/update_user_settings.html", form=form)
