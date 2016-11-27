#!/usr/bin/python
import sys
import logging
from flask import Flask

app = Flask(__name__)

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/Universal-Provisioning-System")

from app import app as application
app.secret_key = 'Add your secret key'
