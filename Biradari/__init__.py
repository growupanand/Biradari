from flask import Flask, session


app = Flask(__name__)
app.secret_key = 'this is secret key'

import Biradari.views
import Biradari.api