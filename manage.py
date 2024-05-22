from src import create_app
from sqlalchemy.orm.mapper import configure_mappers
from src.users import User, ADMIN, ACTIVE, USER, NEW
from src.models import Deck, Post
from src.extensions import db

import os.path
import getpass

app = create_app()

db_path = app.config['SQLALCHEMY_DATABASE_URI'].strip('sqlite:///')
print(db_path)


def initdb():
    """Init/reset database."""

    if not file_exists(db_path):
        db.drop_all()
        configure_mappers()
        db.create_all()
        print("Database initialized + created")

    if input("Create admin ? (yes/no) : ") in "yes":
        admin = User(role_code=ADMIN, status_code=ACTIVE, **get_data("admin"))
        db.session.add(admin)
        db.session.commit()
        print("Admin user created")

    if input("Create user ? (yes/no) :") in "yes":
        user = User(role_code=USER, status_code=ACTIVE, **get_data("user"))
        db.session.add(user)
        db.session.commit()
        print("User created!")

def get_data(per):
    print('*' * 20)
    return {
        'username': input(f"Enter the {per} username: "),
        'email': input(f"Enter the {per} email: "),
        'password': getpass.getpass(f"Enter the {per} password: ")
    }

def file_exists(file):
    return os.path.exists(file)

if __name__ == "__main__":
    with app.app_context():
        initdb()
