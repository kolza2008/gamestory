import os
import time
from flask import *
from app import app, temp_codes
from app.utils import *
from app.models import *
from flask_login import login_required, current_user, login_user, logout_user

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response 

"""@app.route('/send')
def send():
    for i in User.query.all():
        push_notification(i.id, "Biblia")"""

@app.route('/profile')
def profile():
    achieves_users = GetAchieve.query.filter(GetAchieve.user == current_user.id).all()
    achieves = [i for i in Achievement.query.all() if i.id in [j.achieve for j in achieves_users]]
    return render_template('my_profile.html', achievements=achieves)

@app.route('/')
def index_page():
    return render_template('main.html')

@app.route('/sw')
def service_worker():
    return send_file(app.config['PATH_TO_APP']+('app/static/sw.js'), mimetype='application/javascript')

@app.route('/api/games')
def games():
    return jsonify({'main':[i.json for i in Game.query.all()]})

@app.route('/api/users')
def users():
    return jsonify({'main':[i.json for i in User.query.all()]})

@app.route('/game<id_>')
def game_page(id_):
    if'Android' in str(request.user_agent):
        return render_template('game_mobile.html', obj=db.session.query(Game).get(id_))
    return render_template('game.html', obj=db.session.query(Game).get(id_))

@app.route('/mobile/game<id_>')
def mobile(id_):
    return render_template('game_mobile.html', obj=db.session.query(Game).get(id_))

@app.route('/game/photo/<id_>')
def game_photo(id_):
    return send_file(app.config['PATH_TO_APP']+(f'photos/{Game.query.get(id_).photo_name}'))

@app.route('/game/donwload/<id_>')
def game_apk(id_):
    name = Game.query.get(id_).apk_name
    return send_file(app.config['PATH_TO_APP']+(f'applications/{name}'), as_attachment=True, attachment_filename=name)


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    print(request.form.get('object'))
    try:
        obj = NotificationSubscription(
            subscriptiondata=request.form.get('object'),
            userdata = current_user.id
        )
        db.session.add(obj)
        db.session.commit()
        return 'ok'
    except:
        return 'neok'

@app.route('/send')
def test():
    for i in NotificationSubscription.query.all():
        user_subscription = NotificationSubscription.query.filter_by(userdata=i.userdata).first()
        try:
            webpush(
                subscription_info=json.loads(user_subscription.subscriptiondata),
                data="test",
                vapid_private_key='./private_key.pem',
                vapid_claims={
                            'sub': f'mailto:{app.config["ADMIN_EMAIL"]}',
                }
            )
        except WebPushException as ex:
            print('I\'m sorry, Dave, but I can\'t do that: {}'.format(repr(ex)))
            print(ex)
            # Mozilla returns additional information in the body of the response.
            if ex.response and ex.response.json():
                extra = ex.response.json()
                print('Remote service replied with a {}:{}, {}',
                    extra.code,
                    extra.errno,
                    extra.message)

@app.route("/docs")
def docs():
    return render_template('docs.html')

@app.route('/admin')
@admin_required()
def admin():
    return render_template('admin.html')

@app.route('/admin/set_admin')
@admin_required()
def select_set_admin():
    return render_template('set_admin.html')

@app.route('/admin/set_admin/<op_type>/<id_>')
@admin_required(roletype=2)
def set_admin(op_type, id_):
    user = User.query.get(id_)
    user.role = {'uns':0, 'adm':1, 'sup':2}[op_type]
    flash(f'Вы сделали пользователя {user.nick} счастливее')
    return redirect('/admin')

@app.route('/admin/update')
def update_select_game():
    return render_template('update_select.html', obj='update')

@app.route('/admin/update/<id_>', methods=['GET', 'POST'])
@admin_required()
def update_game(id_):
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
    return render_template('update.html', resource=Game.query.get(id_))


@app.route('/admin/achievement')
@admin_required()
def select_game_for_achievement():
    return render_template('update_select.html', obj='achievement')

@app.route('/admin/achievement/<id_>', methods=['GET', 'POST'])
@admin_required()
def new_achievement(id_):
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
    return render_template('new_achievement.html')

@app.route('/achievement/<id_>')
def get_achievement(id_):
    return render_template('achievement.html', obj=Achievement.query.get(id_))

@app.route('/game/achievement/<id_>')
def all_achievements(id_):
    game = Game.query.get(id_)
    achieves = Achievement.query.filter(Achievement.game == game.id).all()
    return render_template('achieves.html', name_game=game.name, achieves=achieves)

@app.route('/admin/new_game', methods=['GET', 'POST'])
@admin_required()
def new_game():
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
                    apk_name=apk_name,
                    secret_value_under=random.randint(0, 1000000),
                    secret_value_top=random.randint(0,1000000))
        db.session.add(game)
        db.session.commit()
        flash('Вы успешно создали игру')
        return render_template('show_codes.html', code_first=game.secret_value_under, code_second=game.secret_value_top)#redirect('/admin')
    return render_template('new_game.html')

@app.route('/admin/delete')
@admin_required(2)
def select_delete_game():
    return render_template('update_select.html', obj='delete')

@app.route('/admin/delete/<id_>')
@admin_required(2)
def delete_game(id_):
    game = Game.query.get(id_)
    db.session.delete(game)
    db.session.commit()
    flash('Игра удалена')
    return redirect('/admin')

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
        user = User(nick=request.form.get('name'), email=request.form.get('email'))
        user.set_password(request.form.get('pass'))
        db.session.add(user)
        db.session.commit()
        flash('Спасибо за регистрацию! Авторизируйтесь')
        return redirect('/login')
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из своего аккаунта")
    return redirect('/login')

@app.route('/vk_entrypoint')
def vk_oauth_handler():
    if request.args:
        user = User.query.filter_by(vk_id=request.args.get('user_id')).first()
        if user:
            temp_codes.update({user.id: request.args.get('access_token')})
            login_user(user)
            return redirect('/')
        else:
            flash('Аккаунта, привязанного к этой учетной записи ВК, не существует')
            return redirect('/register')
    return render_template('vk_code.html')
