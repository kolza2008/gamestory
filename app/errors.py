from app import app
from flask import *
from app.utils import *
from app.models import *


@app.errorhandler(404)
def not_found(e):
    print(e)
    return render_template('not_found.html'), 404

@app.errorhandler(413)
def too_many(e):
    print(e)
    return render_template('too_many.html'), 413