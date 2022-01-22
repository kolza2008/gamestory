import os
from app import app, db
from app.models import User


def admin_user(): 
    if db.session.query(User).filter_by(nick='admin').count() >= 1:
        db.session.delete(db.session.query(User).filter_by(nick='admin').first())
        db.session.commit()
    user = User(nick='admin', role=2)
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()  
    

def set_workspace():
    if not os.path.exists('photos'): os.mkdir('photos')
    if not os.path.exists('applications'): os.mkdir('applications')

set_workspace()
db.create_all()
admin_user()
app.run()