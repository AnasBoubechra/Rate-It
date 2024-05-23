## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
  - [Set Environment Variables](#set-environment-variables)
  - [Add an Admin/User & Initialize the database](#add-an-adminuser--initialize-the-database)
  - [Start the application](#start-the-application)
- [Modules](#modules)
- [Routes](#routes)
- [Screenshots](#screenshots)
- [Author](#author)
- [Support](#support)

## Introduction

**Rate-It** is a *link aggregation* platform centered around the concept of "decks".
Each deck is a collection of related posts, where each post contains a title,
URL, and description.

Posts within a deck can be organized into fields. For example, a "Python
Learning" deck might have fields like "Python Syntax", "Practice", "MOOC", and
"OOP", each containing relevant post entries.

The posts within each field are displayed in a tabular format.

Decks can be set as either public or private. Public decks can be discovered
and shared on the platform's homepage, while private decks are accessible only
to the creator.

Here is an example:
![Example](https://git.cschad.com/rate-it/raw/screenshots/example.webp)

---

## Features

App follows the application factory structure. Which allows you:

* To test. You can have instances of the application with different settings to test every case.
* To deploy multiple instances. Imagine you want to run different versions of the same
  application. Of course you could have multiple instances with different
  configs set up in your webserver, but if you use factories, you can have
  multiple instances of the same application running in the same application
  process which can be handy.

* Sends you an email (in production mode) for 5XX HTTP errors with the actual error.
* Easy to refactor and use the project as a boilertemplate for other projects
* Solid security defaults for cookies / XSS etc (see the config.py)
* Minimal **CSS** / **Js** Uses HTMX only which is about 15kb (compressed)

Note: The app itself doesn't compress responses & Doesn't modify the request headers. This is something
you have to do in the server itself! (Setting CSP headers is important against XSS)

## Installation

Clone the project
```sh
git clone https://git.cschad.com/rate-it.git
cd rate-it
python3 -m venv myvenv
source myvenv/bin/activate
```

Install dependencies in virtualenv
```sh
pip install -r requirements.txt
```

### Set Environment Variables
* The app supports Cloudflare's Captcha! So if you which to use it, add your credentials.

```
export PROJECT_NAME="Rate it"
export SECRET_KEY="My_very_hard_to_guess_secret_key"

export TURNSTILE_SITE_KEY="0x40000000000"
export TURNSTILE_SECRET_KEY="0x400000000000000"

## For /login /signup etc, Mail is needed
export MAIL_SERVER="mail.cschad.com"
export MAIL_PORT="587"
export MAIL_USERNAME="rateit@cschad.com"
export MAIL_PASSWORD="My mail password"
export MAIL_SUBJECT_PREFIX="[Error]"
export MAIL_DEFAULT_RECIPIENT="rateit@cschad.com"
export MAIL_DEFAULT_SENDER='"Rate it" <rateit@cschad.com>'
```
### Add an Admin/User & Initialize the database

The database instance will be created under **./instances/db/*.db**
By default the app will run in development mode!
so a **/db/development.db** will be created.

```py
python manage.py
```
### Start the application
```sh
## Locally
python run.py # Or export FLASK_APP=run.py && flask run

## Or With gunicorn (Production)
gunicorn --workers 4 run:app --bind '0.0.0.0:8000'
```
## Modules
This application uses the following modules:

* Flask
* Flask-SQLAlchemy
* Flask-WTF
* Flask-Mail
* Flask-Login
* Flask-Mailman
* Flask-Admin
* Flask-Htmx
* email_validator
* requests (Only for the /url-check route in posts/routes.py)

## Routes
**Note:** All routes of Flask-Admin have been stripped away!
The app registers three blueprints: (__main__, __posts__, __users__)

* you can access admin interface by adding **/admin** in your base url
```
Endpoint                    Methods           Rule
--------------------------  ----------------  -------------------------------------------------------
main.about                  GET               /about
main.contact_us             GET, POST         /contact-us
main.disclaimer             GET               /disclaimer
main.filter_by              GET               /category/<string:by>
main.filter_by              GET               /category/<string:by>/<int:page>
main.home                   GET               /<int:page>
main.home                   GET               /
main.privacy                GET               /privacy
main.remove                 GET               /remove
main.search                 GET, POST         /search/
main.search                 GET               /search/<string:select>/
main.search                 GET               /search/<string:select>/<int:page>/
main.tac                    GET               /Terms-and-conditions
main.toggle_theme           GET               /toggle-theme
posts.add                   POST              /add/<string:deck_id>
posts.add                   GET               /add/<string:deck_id>/<string:deck_name>
posts.check_url             POST              /check-url
posts.decks                 GET               /decks
posts.decks                 GET               /decks/<int:page>
posts.edit_post             DELETE, GET, PUT  /posts/<string:deck_id>/<string:post_id>/
posts.like                  GET, PUT          /like
posts.new                   GET, POST         /new
posts.rbtn                  PUT               /rbtn
posts.report                GET, POST         /report-deck/<int:deck_id>
posts.single_deck           DELETE, GET, PUT  /deck/<int:deck_id>
posts.table                 GET               /tables/<string:deck_id>/
posts.table                 GET               /tables/<string:deck_id>/<string:deck_name>
posts.table                 GET               /tables/<string:deck_id>/<string:deck_name>/<int:page>/
posts.vote                  PUT               /vote/<string:post_id>/<int:vote_type>
static                      GET               /static/<path:filename>
users.account               GET               /account
users.change_password       GET, POST         /change/password
users.confirm_account       GET, POST         /confirm/account/<secretstring>
users.delete_account        DELETE            /delete/account
users.delete_decks          DELETE            /delete/decks
users.login                 GET, POST         /login
users.logout                GET               /logout
users.reset_password        GET, POST         /reset/password
users.signup                GET, POST         /signup
users.update_settings       GET, POST         /update/settings
users.user_change_password  GET, POST         /change/password/settings
users.user_gravatar         PUT               /user/gravatar
```

## Screenshots
![Image 0](https://git.cschad.com/rate-it/raw/screenshots/img0.webp)
![Image 1](https://git.cschad.com/rate-it/raw/screenshots/img1.webp)
![Image 2](https://git.cschad.com/rate-it/raw/screenshots/img2.webp)

## Author
[CsChad](https://cschad.com)

## Support

[Donation page](https://cschad.com/donate/)
