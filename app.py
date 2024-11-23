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

from datetime import datetime  # Для работы с датами
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
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Новый столбец
    word_count = db.Column(db.Integer)  # Новый столбец


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(300), nullable=False)
    permission = db.Column(db.Integer, default=0)  # Новый столбец (0 - пользователь, 1 - администратор)


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

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if user.permission == 1:  # Администратор
        return redirect(url_for('admin_profile'))
    return redirect(url_for('user_profile'))


@app.route('/user_profile')
@login_required
def user_profile():
    user_id = session['user_id']
    return render_template('user_profile.html')


@app.route('/user_reviews', methods=['GET'])
@login_required
def user_reviews():
    user_id = session['user_id']
    reviews = Revs.query.filter_by(user_id=user_id).all()
    return render_template('user_reviews.html', reviews=reviews)


@app.route('/user_news', methods=['GET'])
@login_required
def user_news():
    user_id = session['user_id']
    sort_by = request.args.get('sort_by', 'date')  # Параметры сортировки
    order = request.args.get('order', 'asc')  # asc - по возрастанию, desc - по убыванию

    if sort_by == 'word_count':
        if order == 'asc':
            news = Post.query.filter_by(user_id=user_id).order_by(Post.word_count.asc()).all()
        else:
            news = Post.query.filter_by(user_id=user_id).order_by(Post.word_count.desc()).all()
    else:  # Сортировка по дате
        if order == 'asc':
            news = Post.query.filter_by(user_id=user_id).order_by(Post.date.asc()).all()
        else:
            news = Post.query.filter_by(user_id=user_id).order_by(Post.date.desc()).all()

    return render_template('user_news.html', news=news)


@app.route('/admin_profile')
@login_required
def admin_profile():
    return render_template('admin_profile.html')


@app.route('/admin_reviews', methods=['GET'])
@login_required
def admin_reviews():
    sort_by = request.args.get('sort_by', 'date')  # Сортировка
    order = request.args.get('order', 'asc')  # Порядок

    if sort_by == 'username':
        reviews = db.session.query(Revs, User).join(User).order_by(
            User.username.asc() if order == 'asc' else User.username.desc()
        ).all()
    else:
        reviews = Revs.query.order_by(
            Revs.date.asc() if order == 'asc' else Revs.date.desc()
        ).all()

    return render_template('admin_reviews.html', reviews=reviews)


@app.route('/admin_news', methods=['GET'])
@login_required
def admin_news():
    sort_by = request.args.get('sort_by', 'date')  # Сортировка
    order = request.args.get('order', 'asc')  # Порядок

    if sort_by == 'username':
        news = db.session.query(Post, User).join(User).order_by(
            User.username.asc() if order == 'asc' else User.username.desc()
        ).all()
    else:
        news = Post.query.order_by(
            Post.date.asc() if order == 'asc' else Post.date.desc()
        ).all()

    return render_template('admin_news.html', news=news)


@app.route('/admin_users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.get(user_id)
        if username:
            user.username = username
        if password:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.commit()
        flash("Информация о пользователе обновлена", "success")

    users = User.query.all()
    return render_template('admin_users.html', users=users)




if __name__ == '__main__':
    app.secret_key = SECRET_KEY#'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)

    app.debug = True
    app.run()


