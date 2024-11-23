from random import randint

from flask import  Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import random
from werkzeug.utils import redirect

from config import SECRET_KEY
from functools import wraps
from flask import session, redirect, url_for, flash


from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash




#  Базы ДАННЫХ VV
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
db = SQLAlchemy(app)

class Revs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)

# БАЗЫ ДАННЫХ ^^

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Войдите в систему, чтобы получить доступ.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    posts = Post.query.all()
    return render_template('posts.html', posts=posts )


@app.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']

        post = Post(title=title, text=text)

        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка при добавлении"
    else:
        return render_template('create.html')


@app.route('/revs')
def revs():
    revs = Revs.query.all()
    return render_template('revs.html', revs=revs )


@app.route('/create_rev', methods=['POST', 'GET'])
@login_required
def create_rev():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        user_id = session['user_id']  # Получаем ID текущего пользователя из сессии

        post = Revs(title=title, text=text, user_id=user_id)

        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка при добавлении"
    else:
        return render_template('create_rev.html')



@app.route('/about')
def about():
    return render_template('about.html')


# Код для инициализации Flask-приложения и БД
# test1@gmail.com test1

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(username=username, email=email, password=hashed_password)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
            return redirect('/login')
        except:
            flash('Ошибка регистрации. Попробуйте другое имя пользователя или email.', 'danger')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Вы успешно вошли!', 'success')
            return redirect('/')
        else:
            flash('Неверный email или пароль.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Вы вышли из системы.', 'info')
    return redirect('/')



if __name__ == '__main__':
    app.secret_key = SECRET_KEY#'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)

    app.debug = True
    app.run()


