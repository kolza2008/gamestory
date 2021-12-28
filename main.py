import time
from flask import *
from flask_sqlalchemy import *
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user


app = Flask(__name__)
app.config['SECRET_KEY'] = '88005553535лучшепозвонитьчемукоготозанимать'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'

lm = LoginManager(app)
lm.login_view = 'login'

db = SQLAlchemy(app)
bs = Bootstrap(app)

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

db.create_all()

if db.session.query(User).filter_by(nick='admin').count() < 1:
    user = User(nick='admin', role=1)
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()


@lm.user_loader
def user_loader(id_):
    return db.session.query(User).get(id_)

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response 


@app.route('/')
def index_page():
    return render_template('main.html', cu=current_user)

@app.route('/api/games')
def games():
    return jsonify({'main':[i.json for i in Game.query.all()]})

@app.route('/game<id_>')
def game_page(id_):
    if request.user_agent.platform == 'Android':
        return render_template('game_mobile.html', obj=db.session.query(Game).get(id_), cu=current_user)
    return render_template('game.html', obj=db.session.query(Game).get(id_), cu=current_user)

@app.route('/mobile/game<id_>')
def mobile(id_):
    return render_template('game_mobile.html', obj=db.session.query(Game).get(id_), cu=current_user)

@app.route('/game/photo/<id_>')
def game_photo(id_):
    return send_file(os.path.abspath(f'photos/{Game.query.get(id_).photo_name}'))

@app.route('/game/donwload/<id_>')
def game_apk(id_):
    name = Game.query.get(id_).apk_name
    return send_file(os.path.abspath(f'applications/{name}'), as_attachment=True, attachment_filename=name)


@app.route('/admin')
@login_required
def admin():
    if current_user.role != 1: return redirect('/login')
    return render_template('admin.html', cu=current_user)

@app.route('/admin/update')
def update_select_game():
    return render_template('update_select.html', cu=current_user)

@app.route('/admin/update/<id_>', methods=['GET', 'POST'])
def update_game(id_):
    if current_user.role != 1: return redirect('/login')
    if request.method == 'POST':
        source = Game.query.get(id_)
        if source.version == request.form.get('version'):
            flash('Такая версия уже была. Смените')
            return redirect(f'/admin/update/{source.id}')
        source.version = request.form.get('version')
        if request.form.get('desc') != source.description: 
            source.description = request.form.get('desc')
        if request.files['photo']: 
            request.files['photo'].save(os.path.join(os.path.abspath('photos'), f"{source.name}.{request.files['photo'].filename.split('.')[-1]}"))
            source.photo_name = f"{source.name}.{request.files['photo'].filename.split('.')[-1]}"
        if request.files['apk']: 
            request.files['apk'].save(os.path.join(os.path.abspath('applications'), f"{source.name.lower().replace(' ', '')}-{source.version}.apk"))
            source.apk_name = f"{source.name.lower().replace(' ', '')}-{source.version}.apk"
        db.session.commit()
        flash('Вы успешно обновили игру')
        return redirect('/admin')
    return render_template('update.html', resource=Game.query.get(id_), cu=current_user)

@app.route('/admin/new_game', methods=['GET', 'POST'])
@login_required
def new_game():
    if current_user.role != 1: return redirect('/login')
    if request.method == 'POST':
        name = request.form.get('name')
        version = request.form.get('version').replace('.', '_') or '1_0'
        photo = request.files['photo']
        apk = request.files['apk']

        photo_name = f"{name}.{photo.filename.split('.')[-1]}"
        apk_name = f"{name.lower().replace(' ', '')}-{version}.apk"

        photo.save(os.path.join(os.path.abspath('photos'), photo_name))
        apk.save(os.path.join(os.path.abspath('applications'), apk_name))

        game = Game(name=name,
                    timestamp=int(time.time()),
                    description=request.form.get('desc').replace('\n', '</br>'),
                    photo_name=photo_name,
                    apk_name=apk_name)
        db.session.add(game)
        db.session.commit()
        flash('Вы успешно создали игру')
        return redirect('/admin')
    return render_template('new_game.html', cu=current_user)
                

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
    return render_template('login.html', cu=current_user)

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
    return render_template('register.html', cu=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из своего аккаунта")
    return redirect('/login')

if __name__ == '__main__':  
    app.run()