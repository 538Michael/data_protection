from app.main import db
from seeders import *


def create_seed():
    add_users(db)
    add_databases(db)
    add_tables(db)
    db.session.commit()
