from flask import Flask
from Biradari import user
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'this is secret key'

def stringtotimestamp(timestamp):
    return datetime.strptime(str(timestamp), "%Y-%m-%d %H:%M:%S.%f")

import Biradari.views
import Biradari.api