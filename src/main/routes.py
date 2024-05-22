from flask import (render_template, request, Blueprint,
                   url_for, flash, abort, session, redirect, current_app)

from flask_login import current_user, user_logged_in

from flask_htmx import make_response as htmx_make_response

from .forms import ContactUsForm

from .models import ContactUs

from ..models import Deck, Post

from ..extensions import db, htmx

from ..modules.http import url_has_allowed_host_and_scheme

from ..utils import (get_user_id, validate_user_input,
                     turnstile_verify)

from sqlalchemy import or_

from ..constants import (
    DECK_TITLE_LENGTH,
    PER_PAGE_POST,
    PER_PAGE_DECK,
    QUERY_LEN_MAX,
    CHOICES
)

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/<int:page>")
def home(page=1):
    deck = Deck.query.filter_by(public=True).order_by(Deck.likes.desc()).\
        paginate(page=page, per_page=PER_PAGE_DECK)

    data = {
        'deck': deck,
        'CHOICES': CHOICES,
        'PER_PAGE_DECK': PER_PAGE_DECK,
        'DECK_TITLE_LENGTH': DECK_TITLE_LENGTH
    }

    return render_template("home.html", **data)

@main.route('/category/<string:by>', defaults={'page': 1})
@main.route("/category/<string:by>/<int:page>")
def filter_by(by=None, page=None):
    if by in CHOICES:
        deck = Deck.query.filter_by(public=True, category=by).\
            paginate(page=page, per_page=PER_PAGE_DECK)
        if not deck.items:
            flash(f"No deck in this Category found!", "notice")
        return render_template('home.html', deck=deck, CHOICES=CHOICES,
                               PER_PAGE_DECK=PER_PAGE_DECK,
                               DECK_TITLE_LENGTH=DECK_TITLE_LENGTH, filter_by=CHOICES[by])
    abort(404)

@main.route('/search/', defaults={'select': 'deck_name', 'page': 1}, methods=['GET', 'POST'])
@main.route('/search/<string:select>/', defaults={'page': 1})
@main.route('/search/<string:select>/<int:page>/')
def search(select, page):
    user_id = get_user_id()
    template="search_decks.html"
    results=None
    per_page=0

    if request.method == "GET":
        query = request.args.get("q", "None")
    elif request.method == "POST":
        select=request.form.get("select")
        query = request.form.get("q", "None")

    try:
        validate_user_input(query, QUERY_LEN_MAX)
    except Exception as e:
        flash(str(e), "error")

    def deck_query():
        global PER_PAGE_DECK
        return per_page, Deck.query.filter(
            (Deck.public == True) | (Deck.user_id == user_id),
            Deck.deck_name.ilike(f'%{query}%')
        ).paginate(page=page, per_page=PER_PAGE_DECK)
    def post_query():
        global PER_PAGE_POST
        return per_page,(
            Post.query
            .join(Deck)
            .filter(
                (Deck.public == True) | (Deck.user_id == user_id),
                or_(
                    (select == 'title' and Post.title.ilike(f'%{query}%')),
                    (select == 'description' and Post.description.ilike(f'%{query}%'))
                )
            )
            .paginate(page=page, per_page=PER_PAGE_POST)
        )

    if select == 'deck_name':
        per_page, results = deck_query()
        template='search_decks.html'
    elif select in ['title', 'description']:
        template='search_posts.html'
        per_page, results = post_query()

    if results is not None:
        if hasattr(results, 'total') and results.total is not None and results.total > 0:
                flash(f"{results.total} result(s) found!", "notice")
        else:
            flash("No results found!", "box")
    return render_template(template, results=results, per_page=per_page,
                           q=query, deck_title_length=DECK_TITLE_LENGTH,
                           PER_PAGE_DECK=PER_PAGE_DECK, select=select)

@main.route("/toggle-theme")
def toggle_theme():
    url = request.referrer or request.host

    if not url_has_allowed_host_and_scheme(url , request.host):
        return abort(400)

    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"
    return redirect(url)

@main.route("/remove")
def remove():
    return ""

@main.route('/contact-us', methods=['GET', 'POST'])
def contact_us():
    form = ContactUsForm()

    if form.validate_on_submit():

        if turnstile_verify():
            _contact = ContactUs()
            form.populate_obj(_contact)
            db.session.add(_contact)
            db.session.commit()
            flash('Thanks! We\'ll get back to you shortly!', 'success')
            return redirect(url_for('main.contact_us'))
        flash("🤖 Captcha verification failed ... Please reload the page and try again.", "error")

    if htmx:
        return render_template('partials/contact_us.html', form=form, htmx=htmx,
                               SITE_KEY=current_app.config['TURNSTILE_SITE_KEY'])
    return render_template('contact_us.html', form=form, htmx=htmx,
                           SITE_KEY=current_app.config['TURNSTILE_SITE_KEY'])

@main.route("/privacy")
def privacy():
    return render_template("/pdt/privacy.html")
@main.route("/disclaimer")
def disclaimer():
    return render_template("/pdt/disclaimer.html")
@main.route("/Terms-and-conditions")
def tac():
    return render_template("/pdt/tac.html")
@main.route("/about")
def about():
    return render_template("about.html")
