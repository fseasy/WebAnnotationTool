
'''
copy from http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
'''

import sqlite3
from flask import g

DATABASE = 'annotation.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()