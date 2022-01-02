import os
from flask import *
from flask_sqlalchemy import *
from flask_login import LoginManager
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config.from_object(os.environ.get('CONFIG') or 'config.ConfigOnTest')

bs = Bootstrap(app)
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'login'

from . import views
from . import models