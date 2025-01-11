import datetime

import requests
from flask import Flask, render_template, redirect, request, flash, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from TestAdd.addTestData import add_test_users
from data import db_session

from data.support import SupportMessage
from forms.user import RegisterForm, LoginForm, ProfileForm

from data.users import User

import base64
#bebra1
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
login_manager = LoginManager()
login_manager.init_app(app)

cur_res = dict()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)



@app.route('/')
@app.route('/home')
def home():
    with db_session.create_session() as db_sess:
        return render_template('main.html')


@app.route('/account')
def profile():
    with db_session.create_session() as db_sess:
        if current_user.is_authenticated:
            cur_user = db_sess.query(User).get(current_user.get_id())
            dct = {}
            if cur_user.notes:
                dct = eval(cur_user.notes)
            return render_template('account.html', user=cur_user, dct=dct)
        return redirect('/login')


@app.route('/account/<int:i>')
def account(i):
    with db_session.create_session() as db_sess:
        dct = {}
        cur_user = db_sess.query(User).filter(User.id == i).first()
        db_sess.close()
        if not cur_user:
            return abort(404)
        if cur_user.test_results:
            dct = eval(cur_user.test_results)
        return render_template('account.html', user=cur_user, dct=dct)


@app.route('/change_profile', methods=['GET', 'POST'])
@login_required
def change_profile():
    with db_session.create_session() as db_sess:
        form = ProfileForm()
        cur_user = db_sess.query(User).get(current_user.get_id())
        if request.method == 'GET':
            form.name.data = cur_user.name
            form.about.data = cur_user.about

        elif request.method == 'POST':
            check = db_sess.query(User).filter(User.name == form.name.data).first()
            if not check or check == cur_user:
                cur_user.name = form.name.data
                cur_user.about = form.about.data
                db_sess.commit()
                return redirect('/account')
            else:
                flash('Пользователь с таким ником уже существует!', 'error')
        db_sess.close()
        return render_template('change_profile.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    with db_session.create_session() as db_sess:
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                flash('Пароли не совпадают!', 'error')
                return render_template('register.html', title='Регистрация', form=form)
            if db_sess.query(User).filter(User.email == form.email.data).first():
                db_sess.close()
                flash('Такой пользователь уже есть!', 'error')
                return render_template('register.html', title='Регистрация', form=form)
            resp = requests.get("https://api.thecatapi.com/v1/images/search").json()[0]["url"]
            user = User(
                is_admin=0,
                name=form.name.data,
                email=form.email.data,
                about=form.about.data,
                cat=resp
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    with db_session.create_session() as db_sess:
        form = LoginForm()
        if form.validate_on_submit():
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            db_sess.close()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            flash('Неправильный логин или пароль!', 'error')
            return render_template('login.html', form=form)
        return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def not_authorized(e):
    return render_template('401.html'), 401


@app.errorhandler(400)
def bad_request(_):
    return render_template('400.html'), 400



@app.route('/admin/')
@login_required
def admin():
    with db_session.create_session() as db_sess:
        user = db_sess.query(User).get(current_user.get_id())
        if user.is_admin != 1:
            flash('У вас нет доступа к этой странице!', 'error')
            return redirect('/')
        else:
            return render_template('admin.html')


@app.route('/admin/delete_profile/<int:i>')
@login_required
def delete_profile(i):
    with db_session.create_session() as db_sess:
        if current_user.is_admin == 1:
            user = db_sess.query(User).filter(User.id == i).first()
            db_sess.delete(user)
            db_sess.commit()
        else:
            flash('У вас нет доступа к этой странице!', 'error')
        return redirect('/')


@app.route('/support', methods=["POST", "GET"])
def support():
    with db_session.create_session() as db_sess:
        if request.method == "POST":
            mes = SupportMessage()
            mes.author_id = current_user.get_id()
            mes.email = request.form.get('email')
            mes.author_name = request.form.get('name')
            mes.message = request.form.get('msg')
            db_sess.add(mes)
            db_sess.commit()
            flash('Сообщение успешно отправлено!', category="success")
            return redirect('/')
        return render_template("support.html")


def main():
    db_session.global_init("db/site_DB.db")
    add_test_users(db_session.create_session())
    app.run(debug=True)


if __name__ == '__main__':
    main()
