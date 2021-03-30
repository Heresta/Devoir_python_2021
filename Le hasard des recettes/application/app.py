from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .constantes import SECRET_KEY
import os

chemin_actuel = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(chemin_actuel, "templates")
statics = os.path.join(chemin_actuel, "static")

app = Flask("application", template_folder=templates, static_folder=statics)

app.config['SECRET_KEY'] = SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../recettes.sqlite'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login = LoginManager(app)

from .routes import generic, api
