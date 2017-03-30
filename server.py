#!python
# -*- coding: utf-8 -*-

import flask
from flask import ( 
                    Flask,
                    render_template
                  )
import db

app = Flask(__name__)



@app.route("/")
def hello_world():
    return 'hello world!'

@app.route("/annotation/<num>")
def annotation(num=1):
    text = num
    cur = db.get_db().cursor()
    

    return render_template("annotation.html", text=text)



@app.teardown_appcontext
def close_connection(exception):
    db.close_connection(exception)