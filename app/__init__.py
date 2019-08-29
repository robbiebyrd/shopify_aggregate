#!/usr/bin/env python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(__name__+'.config.ConfigClass')

login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)
mail = Mail(app)

from app import views
