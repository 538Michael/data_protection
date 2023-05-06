from app.main import db
from seeders import *


def create_seed():
    add_users(db)
    add_valid_databases(db)
    add_databases(db)
    db.session.commit()
