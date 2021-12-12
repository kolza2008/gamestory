import re
from flask import *
from flask_sqlalchemy import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user


app = Flask(__name__)
app.config['SECRET_KEY'] = '88005553535лучшепозвонитьчемукоготозанимать'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'

lm = LoginManager(app)
lm.login_view = 'login'

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    nick = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(365))
    role = db.Column(db.Integer(), default=0)
    def set_password(self, password):
	    self.password_hash = generate_password_hash(password)
    def check_password(self,  password):
	    return check_password_hash(self.password_hash, password)

class Game(db.Model):
    __tablename__ = 'content'
    id = db.Column(db.Integer(), primary_key=True, nullable=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(365), nullable=False)
    photo_name = db.Column(db.String(20), nullable=False)
    apk_name = db.Column(db.String(20), nullable=False)

#db.drop_all()
db.create_all()

@lm.user_loader
def user_loader(id_):
    return db.session.query(User).get(id_)

@app.route('/game<id_>')
def game_page(id_):
    return render_template('game.html', obj=db.session.query(Game).get(id_))


@app.route('/admin')
@login_required
def admin():
    if current_user.role != 1: return redirect('/login')
    return render_template('admin.html')

@app.route('/admin/new_game', methods=['GET', 'POST'])
@login_required
def new_game():
    if current_user.role != 1: return redirect('/login')
    if request.method == 'POST':
        name = request.form.get('name')
        print(request.files)
        photo = request.files['photo']
        apk = request.files['apk']

        photo_name = f"{name}.{photo.filename.split('.')[-1]}"
        apk_name = f"{name.lower().replace(' ', '')}-1_0.apk"

        photo.save(os.path.join(os.path.abspath('photos\\'), photo_name))
        apk.save(os.path.join(os.path.abspath('applications\\'), apk_name))

        game = Game(name=name,
                    description=request.form.get('desc'),
                    photo_name=photo_name,
                    apk_name=apk_name)
        db.session.add(game)
        db.session.commit()
        return redirect('/admin')
    return render_template('new_game.html')
                


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect('/')
    if request.method == 'POST':
        user = User.query.filter_by(nick=request.form.get('name')).first()
        if not user or not user.check_password(request.form.get('pass')):
            flash('Неправильный ник или пароль')
            return redirect('/login')
        login_user(user)
        return redirect('/')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect('/')
    if request.method == 'POST':
        if User.query.filter_by(nick=request.form.get('name')).first():
            flash('Такой пользователь уже существует')
            return redirect('/register')
        user = User(nick=request.form.get('name'))
        user.set_password(request.form.get('pass'))
        db.session.add(user)
        db.session.commit()
        flash('Спасибо за регистрацию! Авторизируйтесь')
        return redirect('/login')
    return render_template('register.html')



app.run()