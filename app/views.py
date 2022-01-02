import os
import time
import random
import string
import datetime
from flask import *
from app import app
from app.models import *
from flask_login import login_required, current_user, login_user, logout_user

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response 

@app.route('/profile')
def profile():
    achieves_users = GetAchieve.query.filter(GetAchieve.user == current_user.id).all()
    print(achieves_users)
    print(Achievement.query.all())
    print([j.achieve for j in achieves_users])
    achieves = [i for i in Achievement.query.all() if i.id in [j.achieve for j in achieves_users]]
    print(achieves)
    return render_template('my_profile.html', achievements=achieves, cu=current_user)

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
    return send_file(app.config['PATH_TO_APP']+(f'photos/{Game.query.get(id_).photo_name}'))

@app.route('/game/donwload/<id_>')
def game_apk(id_):
    name = Game.query.get(id_).apk_name
    return send_file(app.config['PATH_TO_APP']+(f'applications/{name}'), as_attachment=True, attachment_filename=name)


@app.route('/admin')
@login_required
def admin():
    if current_user.role != 1: return redirect('/login')
    return render_template('admin.html', cu=current_user)

@app.route('/admin/update')
def update_select_game():
    return render_template('update_select.html', obj='update', cu=current_user)

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
            request.files['photo'].save(os.path.join(app.config['PATH_TO_APP']+('photos'), f"{source.name}.{request.files['photo'].filename.split('.')[-1]}"))
            source.photo_name = f"{source.name}.{request.files['photo'].filename.split('.')[-1]}"
        if request.files['apk']: 
            request.files['apk'].save(os.path.join(app.config['PATH_TO_APP']+('applications'), f"{source.name.lower().replace(' ', '')}-{source.version}.apk"))
            source.apk_name = f"{source.name.lower().replace(' ', '')}-{source.version}.apk"
        db.session.commit()
        flash('Вы успешно обновили игру')
        return redirect('/admin')
    return render_template('update.html', resource=Game.query.get(id_), cu=current_user)


@app.route('/admin/achievement')
def select_game_for_achievement():
    if current_user.role != 1: return redirect('/login')
    return render_template('update_select.html', obj='achievement', cu=current_user)

@app.route('/admin/achievement/<id_>', methods=['GET', 'POST'])
def new_achievement(id_):
    if current_user.role != 1: return redirect('/login')
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('desc')
        obj = Achievement(
            name = name,
            description =  desc,
            game = Game.query.get(id_).id
        )
        db.session.add(obj)
        db.session.commit()
        return redirect(f'/achievement/{obj.id}')
    return render_template('new_achievement.html', cu=current_user)

@app.route('/achievement/<id_>')
def get_achievement(id_):
    return render_template('achievement.html', obj=Achievement.query.get(id_), cu=current_user)

@app.route('/game/achievement/<id_>')
def all_achievements(id_):
    game = Game.query.get(id_)
    achieves = Achievement.query.filter(Achievement.game == game.id).all()
    return render_template('achieves.html', name_game=game.name, achieves=achieves, cu=current_user)

@app.route('/api/get_achievement/<id_>')
def throw_achievement(id_):
    tok = Token.query.get(request.args.get('token')) 
    if tok and tok.date == str(datetime.date.today()):
        user = User.query.get(tok.user)
        achieve = Achievement.query.get(id_)
        obj = GetAchieve(
            user = user.id,
            achieve = achieve.id
        )
        db.session.add(obj)
        db.session.commit()
        return '200'
    else:
        return Response(status=401)


@app.route('/admin/new_game', methods=['GET', 'POST'])
@login_required
def new_game():
    if current_user.role != 1: return redirect('/login')
    if request.method == 'POST':
        name = request.form.get('name')
        version = (request.form.get('version') or '1_0').replace('.', '_')
        photo = request.files['photo']
        apk = request.files['apk']

        photo_name = f"{name}.{photo.filename.split('.')[-1]}"
        apk_name = f"{name.lower().replace(' ', '')}-{version}.apk"

        photo.save(os.path.join(app.config['PATH_TO_APP']+('photos'), photo_name))
        apk.save(os.path.join(app.config['PATH_TO_APP']+('applications'), apk_name))

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

@app.route('/api/login/token')
def token():
    return ''.join([random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits) for i in range(random.randint(15, 20))])

@app.route('/api/login', methods=['GET', 'POST'])
def login_for_apps():
    if request.method == 'POST':
        user = User.query.filter_by(nick=request.form.get('name')).first()
        if not user or not user.check_password(request.form.get('pass')):
            flash('Неправильный ник или пароль')
            return redirect(f'/api/login?token={request.args.get("token")}')
        try:
            db.session.add(
                Token(
                    token=token,
                    date=str(datetime.date.today()),
                    user = user.id
                )
            )
        except:
            flash('Ваш токен уже существует')
            return redirect(f'/api/login?token={request.args.get("token")}')
        db.session.commit()
        return redirect('/buddy_apps')
    return render_template('login.html', token=request.args.get('token'), cu=current_user)

@app.route('/api/user')
def get_user():
    obj = Token.query.get(request.args.get("token")) 
    if obj and obj.date == str(datetime.date.today()):
        return User.query.get(obj.user).nick
    else:
        return Response(status=401)

@app.route('/buddy_apps')
def buddy():
    return render_template('buddy.html', cu=current_user)

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
