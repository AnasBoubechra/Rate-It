from flask import (render_template, url_for, flash, current_app,
                   redirect, request, Blueprint, abort, session)

from .forms import (PostForm, VoteForm, DeckForm,
                    LikeForm, UrlForm, ReportForm)

from ..models import Post, Deck, if_authorized, update_deck_last_modified

from ..main import ContactUs

from flask_login import login_required, current_user

from flask_htmx import make_response as htmx_make_response

from urllib import request as url_request

from ..extensions import db, htmx

from ..utils import get_user_id, rs, turnstile_verify, validate_table_fields

from ..modules.http import url_has_allowed_host_and_scheme

from ..constants import (
    CHOICES,
    PER_PAGE_POST,
    PER_PAGE_DECK,
    MAX_DECKS_PER_USER,
    MAX_POSTS_PER_DECK,
    DECK_FIELDS_LEN_MAX,
    DECK_DESCRIPTION_LEN_MAX,
)

posts = Blueprint('posts', __name__)

@posts.route("/decks", defaults={'page':1})
@posts.route("/decks/<int:page>")
@login_required
def decks(page):
    deck = Deck.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=PER_PAGE_DECK)
    return render_template('decks.html', deck=deck, PER_PAGE_DECK=PER_PAGE_DECK)

@posts.route("/deck/<int:deck_id>", methods=["DELETE", "PUT", "GET"])
@login_required
def single_deck(deck_id):
    deck = if_authorized(deck_id)
    if request.method == "GET":
        return render_template("partials/edit_deck.html", deck=deck, CHOICES=CHOICES,
                               DECK_DESCRIPTION_LEN_MAX=DECK_DESCRIPTION_LEN_MAX,
                               form=DeckForm(deck_id=deck_id))
    elif request.method == "DELETE":
        db.session.delete(deck)
        db.session.commit()
        return '', 200
    elif request.method == "PUT":
            form=DeckForm()
            changes_made=False
            if form.validate_on_submit():
                if request.args.get('save') == "True":
                    field_names = ['deck_name', 'public', 'deck_description', 'category']
                    for field_name in field_names:
                        if field_name == 'public':
                            if form.public.data != deck.public:
                                public_value = True if form.public.data else False
                                setattr(deck, field_name, public_value)
                                changes_made = True
                        elif field_name in request.form and getattr(deck, field_name) != request.form[field_name]:
                            setattr(deck, field_name, rs(request.form[field_name]))
                            changes_made = True
                    if changes_made:
                        db.session.commit()
                return render_template("partials/deck_item.html", deck=deck)
            return render_template("partials/edit_deck.html", deck=deck, form=form, CHOICES=CHOICES,
                                   DECK_DESCRIPTION_LEN_MAX=DECK_DESCRIPTION_LEN_MAX)

@posts.route("/posts/<string:deck_id>/<string:post_id>/", methods=['GET', 'PUT', 'DELETE'])
@login_required
def edit_post(deck_id,post_id):
    deck = if_authorized(deck_id)
    post = Post.query.get(post_id)
    if not post or current_user.id != post.user_id:
        abort(403, "You are not allowed to perform any action on this post ...")
    form = PostForm()
    form.field.choices=deck.fields_choices()

    fields =  dict(post.__dict__)
    if request.method == "GET":
        if request.args.get('s') == "post-options":
            return render_template("partials/edit_post_options.html", post=post, deck=deck)
        return render_template("partials/edit_post.html", post=post, deck=deck, form=form)
    elif request.method == "DELETE":
        update_deck_last_modified(deck)
        db.session.delete(post)
        db.session.commit()
        return '', 200
    elif request.method == "PUT":
        if form.validate_on_submit():
            if request.args.get('save') == "True":
                for field_name in fields:
                    if field_name in request.form and getattr(post, field_name) != request.form[field_name]:
                        setattr(post, field_name, rs(request.form[field_name]))
                        update_deck_last_modified(deck)
                        db.session.commit()
            return render_template("partials/post_item.html", post=post, deck=deck, form=form)
        return render_template("partials/edit_post.html", post=post, deck=deck, form=form)

@posts.route("/add/<string:deck_id>", methods=['POST'], defaults={'deck_name':None})
@posts.route("/add/<string:deck_id>/<string:deck_name>")
def add(deck_id, deck_name):
    deck = if_authorized(deck_id)
    site_key=current_app.config['TURNSTILE_SITE_KEY']
    form = PostForm()

    form.field.choices = deck.fields_choices()
    if request.method == 'POST':
        if form.validate_on_submit():
            if get_user_id() == 1000 and not turnstile_verify():
                flash("Ooopsii Captcha verification failed ... 🤖 Please Try again!", "error")
                if htmx:
                    return render_template("partials/add.html", form=form, deck=deck, htmx=htmx)
                return render_template('add.html', form=form, deck=deck, htmx=htmx)

            if len(deck.posts) >= MAX_POSTS_PER_DECK:
                flash(f"This deck reached the maximum number of possible posts! Which is {MAX_POSTS_PER_DECK} posts per deck", "error")
                return redirect(url_for('posts.table', deck_id=deck.id, deck_name=deck.formatted_deck_name()))

            post = Post(
                user_id=get_user_id(),
                deck_id=deck_id,
                field=form.field.data,
                title=rs(form.title.data),
                description=rs(form.description.data),
                url=form.url.data
            )
            try:
                update_deck_last_modified(deck)
                db.session.add(post)
                db.session.commit()
                flash('Post created! Thanks for your contribution', 'success')
                return redirect(url_for('posts.table', deck_id=deck.id, deck_name=deck.formatted_deck_name()))
            except Exception as e:
                return f"{str(e)}"
    if htmx:
        return render_template("partials/add.html", form=form, deck=deck, htmx=htmx, site_key=site_key)
    return render_template('add.html', form=form, deck=deck, htmx=htmx, site_key=site_key)

@posts.route("/new", methods=['GET', 'POST'])
@login_required
def new():
    form = DeckForm()
    if form.validate_on_submit():

        if len(current_user.decks) >= MAX_DECKS_PER_USER:
            flash("You reached the maximum number of decks :/", "error")
            flash(f"You account can only have up to {MAX_DECKS_PER_USER} decks", "error")
            return redirect(url_for('posts.decks'))

        deck = Deck(
            user_id=current_user.id,
            deck_name=rs(form.deck_name.data),
            deck_description=rs(form.deck_description.data) if form.deck_description.data else '',
            category=rs(form.category.data),
            fields=rs(form.fields.data),
            public=form.public.data
        )
        try:
            db.session.add(deck)
            db.session.commit()
            flash('Deck added!', 'success')
            return redirect(url_for('posts.decks'))
        except:
            flash("There was a problem :/", "error")
    if htmx:
        return render_template("partials/new.html", form=form, htmx=htmx)
    return render_template("new.html", form=form, htmx=htmx,
                           DECK_FIELDS_LEN_MAX=DECK_FIELDS_LEN_MAX)

@posts.route('/tables/<string:deck_id>/', defaults={'page': 1, 'deck_name': None})
@posts.route('/tables/<string:deck_id>/<string:deck_name>', defaults={'page': 1})
@posts.route('/tables/<string:deck_id>/<string:deck_name>/<int:page>/')
def table(deck_id, deck_name, page):
    deck = if_authorized(deck_id)
    url = url_for('posts.table', deck_id=deck.id, deck_name=deck.formatted_deck_name())

    s = request.args.get('s')
    if s:
        if s == "table-options":
            return render_template("partials/table-options.html", deck=deck)
        elif s == "share":
            if deck.public:
                return render_template("partials/share.html", deck=deck)
            flash("This Deck is private! Please make sure you make it public if you wish to share it.", "notice")
            return htmx_make_response(location=url)

    form=PostForm()
    like=session.get(f'like-{deck.id}')
    unique_field_values, posts=Post.get_unique_field_per_page(deck_id)
    posts=posts.paginate(page=page, per_page=PER_PAGE_POST, error_out=False)

    if deck_name != deck.formatted_deck_name():
        return redirect(url)
    return render_template('user_tables.html', form=form, deck=deck, PER_PAGE_POST=PER_PAGE_POST,
                           posts=posts, like=like, unique_field_values=unique_field_values)

@posts.route("/rbtn", methods=["PUT"])
@login_required
def rbtn():
    fields = rs(request.form.get('fields'))

    if fields:
        try:
            validate_table_fields(fields)
            buttons = ''.join(f'<button class="m-8" disabled>{word}</button>' for word in fields.split())
            return render_template("partials/rbtn.html", buttons=buttons, l=len(fields.split()))
        except ValueError as e:
            return f"""<span class="ft">{str(e)}</span>"""
    abort(400)

@posts.route("/check-url", methods=["POST"])
def check_url():
    form=UrlForm()
    if form.validate_on_submit():
        url = request.form.get('url')
        try:
            req = url_request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with url_request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    return render_template("partials/url_status_success.html", status_code=200)
                else:
                    return render_template("partials/url_status_success.html", status_code=response.status)
        except url_request.HTTPError as e:
            return render_template("partials/url_status.html", error_message=f"URL returned a '{e.code}' code: {e.reason}")
        except url_request.URLError as e:
            return render_template("partials/url_status.html", error_message=f"Failed to connect to URL: {e.reason}")
    return render_template("partials/url_status.html", error_message=f"Invalid Url")

@posts.route("/like", methods=["PUT", "GET"])
def like():
    form = LikeForm()
    if form.validate_on_submit():
        like_id = request.form.get('like_id')
        deck = if_authorized(like_id)
        slike=f'like-{like_id}'
        if htmx:
            if deck is not None:
                if session.get(slike) == 1:
                    deck.likes -=1
                    clk="like"
                elif session.get(slike) == 0 or session.get(slike) is None:
                    deck.likes +=1
                    clk="liked"
                db.session.commit()
                session[slike] = 1 - session.get(slike) if session.get(slike) is not None else 1
                return render_template("partials/like.html", deck=deck, like=session[slike])
        return redirect(url_for('main.home'))

@posts.route("/vote/<string:post_id>/<int:vote_type>", methods=["PUT"])
def vote(post_id, vote_type):
    post = Post.query.get_or_404(post_id)

    if not url_has_allowed_host_and_scheme(request.referrer, request.host):
        return abort(400)

    if get_user_id() != 1000:
        if current_user.id != post.user_id:
            if int(vote_type) == 1:
                post.votes += 1
            elif int(vote_type) == 0:
                post.votes -= 1
            db.session.commit()
        flash("You can't upvote or down vote your own posts :)", "notice")
        return htmx_make_response(location=url_for('users.login', next=request.referrer))
    flash("You need to be logged in to vote", "notice")
    return htmx_make_response(location=url_for('users.login', next=request.referrer))

@posts.route("/report-deck/<int:deck_id>", methods=['GET', 'POST'])
def report(deck_id):
    deck = if_authorized(deck_id)
    form = ReportForm()
    user_id = get_user_id()
    if  get_user_id() == deck.user.id:
        return "That's your own deck 🙃"
    elif get_user_id() == 1000:
        return htmx_make_response(redirect=url_for('users.login', next=f"/report-deck/{deck_id}"))

    if form.validate_on_submit():
        _ticket = ContactUs(name=current_user.username,
                             email=current_user.email,
                             deck_id=form.deck_id.data,
                             subject=form.reason.data,
                             message=form.description.data)
        db.session.add(_ticket)
        db.session.commit()

        flash("Thank you for your feedback .. We'll check that as soon as possible", "success")
        return htmx_make_response(refresh=True)
    return render_template("partials/report.html", form=form, deck_id=deck_id)
