import os
import time
import random
import string
import datetime
from flask import *
from flask_sqlalchemy import *
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user

app = Flask(__name__)
app.config.from_object('config.ConfigOnTest')

db = SQLAlchemy(app)
bs = Bootstrap(app)
lm = LoginManager(app)
lm.login_view = 'login'

from . import views
from . import models