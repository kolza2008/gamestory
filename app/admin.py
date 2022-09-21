from flask import *
from app import app, db
import os
import time
from app.utils import *
from app.models import *

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

        print(request.form)
        print(game.id, request.form.get('price'))

        try:
            price = float(request.form.get('price'))
        except:
            price = 0.0 

        fin = GameFinance(game = game.id, 
                          price = price,
                          discount = '')
        db.session.add(fin)
        db.session.commit()

        flash('Вы успешно создали игру')
        return render_template('show_codes.html', code_first=game.secret_value_under, code_second=game.secret_value_top, product=game.secret_product)#redirect('/admin')
    return render_template('new_game.html')

@app.route('/admin/new_user', methods=['GET', 'POST'])
@admin_required(2)
def create_admin_user():
    if request.method == 'POST':
        if User.query.filter_by(nick=request.form.get('name')).first():
            flash('Такой пользователь уже существует')
            return redirect('/admin/new_user')
        user = User(nick=request.form.get('name'), role=int(request.form.get('role')))
        user.set_password(request.form.get('pass'))
        db.session.add(user)
        db.session.commit()
        flash(f'Админ аккаунт {user.nick} есть')
        return redirect('/admin')
    return render_template('new_admin.html')

@app.route('/admin/user_delete')
@admin_required(2)
def user_delete_select():
    return render_template('user_select.html', obj='user_delete')

@app.route('/admin/user_delete/<id_>')
@admin_required(2)
def user_delete(id_):
    user = User.query.get(id_)
    db.session.delete(user)
    db.session.commit()
    flash(f'Пользователь с ником {user.nick} был удален')
    return redirect('/admin')

@app.route('/admin/show_codes')
@admin_required(2)
def show_codes():
    return render_template('update_select.html', obj='show_codes')

@app.route('/admin/show_codes/<id_>')
@admin_required(2)
def show_code(id_):
    source = Game.query.get(id_)
    return render_template('show_codes.html', code_first=source.secret_value_under, code_second=source.secret_value_top, product=source.secret_product)

@app.route('/admin/delete')
@admin_required(2)
def select_delete_game():
    return render_template('update_select.html', obj='delete')

@app.route('/admin/delete/<id_>')
@admin_required(2)
def delete_game(id_):
    game = Game.query.get(id_)
    db.session.delete(game)
    #os.remove(os.path.join(app.config['PATH_TO_APP']+('photos'), game.photo_name))
    #os.remove(os.path.join(app.config['PATH_TO_APP']+('applications'), game.apk_name))
    db.session.commit()
    flash('Игра удалена')
    return redirect('/admin')


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
        if request.form.get('desc') and request.form.get('desc') != source.description: 
            source.description = request.form.get('desc')
        if request.files['photo']: 
            request.files['photo'].save(os.path.join(app.config['PATH_TO_APP']+('photos'), f"{source.name}.{request.files['photo'].filename.split('.')[-1]}"))
            source.photo_name = f"{source.name}.{request.files['photo'].filename.split('.')[-1]}"
        if request.files['apk']: 
            request.files['apk'].save(os.path.join(app.config['PATH_TO_APP']+('applications'), f"{source.name.lower().replace(' ', '')}-{source.version}.apk"))
            source.apk_name = f"{source.name.lower().replace(' ', '')}-{source.version}.apk"
        if request.form.get('price') and request.form.get('price') != source.price:
            source.price = float(request.form.get('price'))
        db.session.commit()
        flash('Вы успешно обновили игру')
        return redirect('/admin')
    return render_template('update.html', resource=Game.query.get(id_))
