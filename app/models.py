from app import db, lm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    nick = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(365))
    vk_id = db.Column(db.Integer(), default=(-1))
    role = db.Column(db.Integer(), default=0)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self,  password):
	    return check_password_hash(self.password_hash, password)

@lm.user_loader
def user_loader(id_):
    return db.session.query(User).get(id_)

class Game(db.Model):
    __tablename__ = 'content' 
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    name = db.Column(db.String(20), nullable=False)
    version = db.Column(db.String(20), default='1.0')
    timestamp = db.Column(db.Integer())
    description = db.Column(db.String(365), nullable=False)
    photo_name = db.Column(db.String(20), nullable=False)
    apk_name = db.Column(db.String(20), nullable=False)
    @property
    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'timestamp': self.timestamp,
            'description': self.description,
            'photo_name': self.photo_name,
            'apk_name': self.apk_name
        }

class Token(db.Model):
    __tablename__ = 'tokens'
    token = db.Column(db.String(20), primary_key=True)
    date = db.Column(db.String(15))
    address = db.Column(db.String(15))
    useragent = db.Column(db.String(128))
    user = db.Column(db.Integer(), db.ForeignKey('users.id'))

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    name = db.Column(db.String(24))
    description = db.Column(db.String(64))
    game = db.Column(db.Integer(), db.ForeignKey('content.id'))
    def __repr__(self):
        return f'Ачивка {self.id}'
    #screenshot = db.Column(db.String(128))

class GetAchieve(db.Model):
    __tablename__ = 'achieves'
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    user = db.Column(db.Integer(), db.ForeignKey('users.id'))
    achieve = db.Column(db.Integer(), db.ForeignKey('achievements.id'))
    def __repr__(self):
        return f'Пользователь {self.user} получил ачивку {self.achieve}'

class NotificationSubscription(db.Model):
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    subscriptiondata = db.Column(db.String(512))
    userdata = db.Column(db.Integer(), db.ForeignKey('users.id'))