import os
import platform
from flask import *
from flask_cors import *
from flask_mail import Mail 
from flask_sqlalchemy import *
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
import logging


app = Flask(__name__)
if platform.system() == 'Windows':
    app.config.from_object(os.environ.get('CONFIG') or 'config.ConfigOnTest')
else:
    app.config.from_object('config.ConfigOnServer')

mail = Mail(app)
cors = CORS(app)
bs = Bootstrap(app)
db = SQLAlchemy(app)
migr = Migrate(app, db)
lm = LoginManager(app)
lm.login_view = 'login'

temp_token = {}
temp_codes = {}

tokenlog = logging.getLogger('apitokens')

from . import views
from . import errors
from . import models
from . import apiroutes
from . import citelstrike
