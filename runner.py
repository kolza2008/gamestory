import os
import platform
from app import app, db
from app.models import User, Game


def admin_user(): 
    if db.session.query(User).filter_by(nick='admin').count() >= 1:
        db.session.delete(db.session.query(User).filter_by(nick='admin').first())
        db.session.commit()
    user = User(nick='admin', role=2)
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()  
    

def set_workspace():
    if not os.path.exists('zips'): os.mkdir('zips')
    if not os.path.exists('photos'): os.mkdir('photos')
    if not os.path.exists('applications'): os.mkdir('applications')

def print_products():
    for i in Game.query.all():
        print(i.name, i.secret_product)

print(platform.system())

set_workspace()
db.create_all()
admin_user()
print_products()
app.run() 