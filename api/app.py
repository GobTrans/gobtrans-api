# -*- coding: utf-8 -*-
from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('settings.py')
