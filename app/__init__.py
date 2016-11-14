from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, SubmitField
from wtforms.validators import Required

# Create flask app
app = Flask(__name__)
# Set config file location
app.config.from_object('config')
# Create database app
db = SQLAlchemy(app)
# Create login app
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
# Defer our logic to the view file
from app import views, models, db, app

# Simple startup script for the application
if __name__ == '__main__':
    app.run()
