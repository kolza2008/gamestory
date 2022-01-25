from app.models import Token
from app import db

for i in Token.query.all():
    db.session.delete(i)

db.session.commit()