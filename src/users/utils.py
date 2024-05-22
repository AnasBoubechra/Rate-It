from flask import current_app, url_for, render_template, abort, flash
from flask_mailman import EmailMultiAlternatives
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        msg.send(msg)

def send_email(subject, html, text, to):
    msg = EmailMultiAlternatives(
        subject, text,
        current_app.config['MAIL_DEFAULT_SENDER'],
        [to]
    )
    msg.attach_alternative(html, "text/html")
    thr = Thread(target=send_async_email, args=[current_app._get_current_object(), msg])
    thr.start()
    return thr

def generate_hash(raw, salt):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=salt)
    return serializer.dumps(raw)

def get_data_from_hash(hash, salt):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=salt)
    try:
        return serializer.loads(hash, max_age=current_app.config['TOKEN_MAX_AGE_SECONDS'])
    except:
        flash("Expired or non valid token!", "error")
        abort(400, description="<strong>Invalid or Expired link:</strong> Please make \
              sure you use the latest link received in your <u>Inbox</u>.")

def confirm_user_mail(name, email, subject, html, text):
    key = generate_hash([name, email], salt="confirm_account")
    subject = f'{subject}' + current_app.config['PROJECT_NAME']
    url = url_for('users.confirm_account', secretstring=key, _external=True)
    html = render_template(html, project=current_app.config['PROJECT_NAME'], url=url, name=name)
    text = render_template(text, project=current_app.config['PROJECT_NAME'], url=url, name=name)

    send_email(subject, html, text, email)
