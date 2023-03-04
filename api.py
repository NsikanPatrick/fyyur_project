import json
import sys
from tkinter import N
import dateutil.parser
import babel
from flask import Flask, jsonify, request, Response, flash, redirect, url_for, abort
from flask_cors import CORS
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import null
from forms import *
from models import *


# app = Flask(__name__)
# CORS(app)

app = Flask(__name__)
moment = Moment(app)
db = db_setup(app)

def create_app(test_config=None):
    app = Flask(__name__)
#   CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers 
    # fter the request is recieved, run the method beneath
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    
    @app.route('/messages')
    @cross_origin()
    def get_messages():
        return 'GETTING MESSAGES'

@app.route('/')
def greeting():
    return jsonify({"Greeting": "Hello world!"})

@app.route('/multiply/<int:id>')
# you can now goto curl http://127.0.0.1:5000/multiply/5 on the power shell
def get_multiplication(id):
    res = id*10
    if res:
        return jsonify({"success": True, "message": res})
    else:
        abort(404)

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    # data = []
    venues = Venue.query.all()
    formatted_values = [venues.format() for venue in venues]
    if venues:
        return jsonify({
            'success': True,
            'result': formatted_values
        })
    else:
        abort(404)


if __name__ == '__main__':
    app.run()
    