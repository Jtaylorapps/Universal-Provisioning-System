import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Toggle debug information. Must be False when in production.
DEBUG = False

# Flask-WTF configuration
WTF_CSRF_ENABLED = True
SECRET_KEY = 'ups_development_key'

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Number of table rows to show per page
RESULTS_PER_PAGE = 10
