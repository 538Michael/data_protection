from app.main import db
from seeders import *


def create_seed():
    add_users(db)
    db.session.commit()
