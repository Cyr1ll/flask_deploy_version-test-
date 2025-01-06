from random import randint

from flask import  Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import random
from werkzeug.utils import redirect

from config import SECRET_KEY
from functools import wraps
from flask import session, redirect, url_for, flash, request, flash

from datetime import datetime, date,timedelta  # Для работы с датами
from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from flask_migrate import Migrate, migrate
from faker import Faker
import random

from extensions import db
from models import TestDB
import os
import pandas as pd

import csv
import io
from flask import make_response

import sklearn
from sklearn.preprocessing import MinMaxScaler

#  Базы ДАННЫХ VV
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newflask.db'
db.init_app(app)
#db = SQLAlchemy(app)
migrate = Migrate(app,db)

class Revs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Связь с пользователем
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Дата написания
    word_count = db.Column(db.Integer)  # Количество слов в отзыве


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
    user_id = db.Column(db.Integer, nullable=False)
    word_count = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Новое поле

    def recalculate_word_count(self):
        self.word_count = len(self.text.split())



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
        user_id = session['user_id']

        # Подсчет количества слов в тексте
        word_count = len(text.split())

        # Создаем новый пост
        post = Post(title=title, text=text, user_id=user_id, word_count=word_count)

        try:
            db.session.add(post)
            db.session.commit()
            flash("Новость успешно добавлена!", "success")
            return redirect('/user_profile')
        except:
            flash("Ошибка при добавлении новости", "danger")
            return redirect('/create')
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
        user_id = session['user_id']  # ID текущего пользователя
        word_count = len(text.split())  # Подсчет количества слов

        # Создание отзыва
        review = Revs(title=title, text=text, user_id=user_id, word_count=word_count)

        try:
            db.session.add(review)
            db.session.commit()
            flash("Отзыв успешно добавлен!", "success")
            return redirect('/revs')
        except:
            flash("Ошибка при добавлении отзыва.", "danger")
            return redirect('/create_rev')
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
            session['permission'] = user.permission
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
    user_id = session.get('user_id')  # Получаем ID текущего пользователя
    user = User.query.filter_by(id=user_id).first()  # Находим пользователя в базе данных

    if not user:
        flash("Пользователь не найден.", "danger")
        return redirect('/')

    if user.permission == 1:  # Если администратор
        return redirect(url_for('admin_profile'))
    else:  # Если обычный пользователь
        return redirect(url_for('user_profile'))


    # user = User.query.get(session['user_id'])
    # if user.permission == 1:  # Администратор
    #     return redirect(url_for('admin_profile'))
    # return redirect(url_for('user_profile'))


@app.route('/user_profile')
@login_required
def user_profile():
    user_id = session['user_id']
    user_permission = session['permission']
    sort_by = request.args.get('sort_by', 'date')  # Получаем критерий сортировки из запроса
    order = request.args.get('order', 'desc')     # Получаем порядок сортировки
    test_db_records = TestDB.query.filter_by(user_id=user_id).all()

    user_reviews=Revs.query.filter_by(user_id=user_id).all()

    if sort_by == 'words':
        if order == 'asc':
            user_posts = Post.query.filter_by(user_id=user_id).order_by(Post.word_count.asc()).all()
        else:
            user_posts = Post.query.filter_by(user_id=user_id).order_by(Post.word_count.desc()).all()
    else:
        if order == 'asc':
            user_posts = Post.query.filter_by(user_id=user_id).order_by(Post.date.asc()).all()
        else:
            user_posts = Post.query.filter_by(user_id=user_id).order_by(Post.date.desc()).all()


    return render_template('user_profile.html', posts=user_posts, revs=user_reviews, id=user_id, perm=user_permission, test_db_records=test_db_records)


@app.route('/admin_profile')
@login_required
def admin_profile():
    # Проверяем, что пользователь - администратор
    user_id = session['user_id']
    user = User.query.get(user_id)
    if user.permission != 1:
        flash("Доступ запрещен!", "danger")
        return redirect('/')

    # Получение параметров сортировки и поиска
    review_sort_by = request.args.get('review_sort_by', 'date')
    review_order = request.args.get('review_order', 'desc')
    news_sort_by = request.args.get('news_sort_by', 'date')
    news_order = request.args.get('news_order', 'desc')

    # Параметры поиска
    news_title_filter = request.args.get('news_title', '')
    news_text_filter = request.args.get('news_text', '')
    review_title_filter = request.args.get('review_title', '')
    review_text_filter = request.args.get('review_text', '')
    user_id_filter = request.args.get('user_id', '')
    user_name_filter = request.args.get('user_name', '')

    # Фильтрация и сортировка новостей
    posts_query = Post.query
    if news_title_filter:
        posts_query = posts_query.filter(Post.title.ilike(f"%{news_title_filter}%"))
    if news_text_filter:
        posts_query = posts_query.filter(Post.text.ilike(f"%{news_text_filter}%"))
    if news_sort_by == 'words':
        posts_query = posts_query.order_by(Post.word_count.asc() if news_order == 'asc' else Post.word_count.desc())
    else:
        posts_query = posts_query.order_by(Post.date.asc() if news_order == 'asc' else Post.date.desc())
    posts = posts_query.all()

    # Фильтрация и сортировка отзывов
    reviews_query = Revs.query
    if review_title_filter:
        reviews_query = reviews_query.filter(Revs.title.ilike(f"%{review_title_filter}%"))
    if review_text_filter:
        reviews_query = reviews_query.filter(Revs.text.ilike(f"%{review_text_filter}%"))
    if review_sort_by == 'words':
        reviews_query = reviews_query.order_by(Revs.word_count.asc() if review_order == 'asc' else Revs.word_count.desc())
    else:
        reviews_query = reviews_query.order_by(Revs.date.asc() if review_order == 'asc' else Revs.date.desc())
    reviews = reviews_query.all()

    # Фильтрация пользователей
    users_query = User.query.filter(User.permission == 0)
    if user_id_filter.isdigit():
        users_query = users_query.filter(User.id == int(user_id_filter))
    if user_name_filter:
        users_query = users_query.filter(User.username.ilike(f"%{user_name_filter}%"))
    users = users_query.all()

    return render_template(
        'admin_profile.html',
        posts=posts,
        reviews=reviews,
        users=users,
        review_sort_by=review_sort_by,
        review_order=review_order,
        news_sort_by=news_sort_by,
        news_order=news_order
    )




@app.route('/edit_news/<int:news_id>', methods=['GET', 'POST'])
@login_required
def edit_news(news_id):
    if session.get('permission') != 1:
        flash("У вас нет доступа к этой странице.", "danger")
        return redirect('/')

    news = Post.query.get_or_404(news_id)

    if request.method == 'POST':
        news.title = request.form['title']
        news.text = request.form['text']
        news.recalculate_word_count()
        db.session.commit()
        flash("Новость успешно обновлена.", "success")
        return redirect(url_for('admin_profile'))

    return render_template('edit_news.html', news=news)


@app.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    if session.get('permission') != 1:
        flash("У вас нет доступа к этой странице.", "danger")
        return redirect('/')

    review = Revs.query.get_or_404(review_id)

    if request.method == 'POST':
        review.title = request.form['title']
        review.text = request.form['text']
        db.session.commit()
        flash("Отзыв успешно обновлен.", "success")
        return redirect(url_for('admin_profile'))

    return render_template('edit_review.html', review=review)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if session.get('permission') != 1:
        flash("У вас нет доступа к этой странице.", "danger")
        return redirect('/')

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        db.session.commit()
        flash("Пользователь успешно обновлен.", "success")
        return redirect(url_for('admin_profile'))

    return render_template('edit_user.html', user=user)


@app.route('/view_test_db')
@login_required
def view_test_db():
    user_id = session.get('user_id')
    test_db = TestDB.query.filter_by(user_id=user_id).all()
    return render_template('test_db.html', test_db_records=test_db)


faker = Faker()

@app.route('/test_db', methods=['GET', 'POST'])
@login_required
def test_db():
    user_id = session.get('user_id')

    # Проверяем, есть ли уже записи в TestDB для текущего пользователя
    existing_records = TestDB.query.filter_by(user_id=user_id).all()

    if not existing_records:
        # Генерация 10 случайных записей
        for _ in range(10):
            new_record = TestDB(
                user_id=user_id,
                purchase_amount=round(random.uniform(10, 500), 2),
                purchase_date=date.today() - timedelta(days=random.randint(1, 365)),
                customer_name=faker.name()
            )
            db.session.add(new_record)
        db.session.commit()
        flash("Тестовая БД успешно создана!", "success")

    # Переход на страницу с отображением тБД
    return redirect(url_for('view_test_db'))


@app.route('/edit_test_db/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_test_db_record(record_id):
    record = TestDB.query.get_or_404(record_id)
    current_user_id = session.get('user_id')
    current_user = User.query.get_or_404(current_user_id)

    # Проверка доступа: владелец записи или администратор
    if record.user_id != current_user_id and current_user.permission != 1:
        flash("Вы не можете редактировать эту запись", "danger")
        return redirect(url_for('test_db'))

    if request.method == 'POST':
        record.customer_name = request.form['customer_name']
        record.purchase_amount = request.form['purchase_amount']
        record.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d')
        db.session.commit()
        flash("Запись успешно обновлена", "success")
        return redirect(url_for('test_db') if current_user.permission == 0 else url_for('edit_test_db_user', user_id=record.user_id))

    return render_template('edit_test_db.html', record=record)


@app.route('/add_test_db_record', methods=['POST'])
@login_required
def add_test_db_record():
    customer_name = request.form['customer_name']
    purchase_amount = request.form['purchase_amount']
    purchase_date = request.form['purchase_date']

    new_record = TestDB(
        customer_name=customer_name,
        purchase_amount=purchase_amount,
        purchase_date=datetime.strptime(purchase_date, '%Y-%m-%d'),
        user_id=session['user_id']
    )
    db.session.add(new_record)
    db.session.commit()
    flash("Запись успешно добавлена", "success")
    return redirect(url_for('test_db'))

@app.route('/delete_test_db_record/<int:record_id>', methods=['GET'])
@login_required
def delete_test_db_record(record_id):
    record = TestDB.query.get_or_404(record_id)
    current_user_id = session.get('user_id')
    current_user = User.query.get_or_404(current_user_id)

    # Проверка доступа: владелец записи или администратор
    if record.user_id != current_user_id and current_user.permission != 1:
        flash("Вы не можете удалить эту запись", "danger")
        return redirect(url_for('test_db'))

    db.session.delete(record)
    db.session.commit()
    flash("Запись успешно удалена", "success")
    return redirect(url_for('test_db') if current_user.permission == 0 else url_for('edit_test_db_user', user_id=record.user_id))


@app.route('/download_test_db')
@login_required
def download_test_db():
    # Получение тестовой БД пользователя
    user_id = session['user_id']
    test_db = TestDB.query.filter_by(user_id=user_id).all()

    # Создание CSV-буфера в памяти
    output = io.StringIO()
    writer = csv.writer(output)

    # Добавление заголовков CSV
    writer.writerow(["customer_name", "purchase_amount", "purchase_date"])

    # Добавление записей из тестовой БД
    for record in test_db:
        writer.writerow([record.customer_name, record.purchase_amount, record.purchase_date])

    # Получение содержимого CSV
    csv_data = output.getvalue()
    output.close()

    # Создание HTTP-ответа с CSV-данными
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=test_db.csv"
    response.headers["Content-Type"] = "text/csv"

    return response

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/preliminary_analysis', methods=['GET', 'POST'])
@login_required
def preliminary_analysis():
    if request.method == 'POST':
        # Проверка наличия файла в запросе
        if 'file' not in request.files:
            flash('Файл не выбран')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Имя файла не указано')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Сохраняем файл
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            # Анализ файла
            try:
                df = pd.read_csv(filename)
                print("Данные из файла загружены(prelim):", df.head())  # Для отладки
                result, processing_time = analyze_uploaded_file(df)
                return render_template('analysis_result.html', result=result, processing_time=processing_time)
            except Exception as e:
                flash(f'Ошибка при обработке файла: {e}')
                return redirect(request.url)
    return render_template('preliminary_analysis.html')


def analyze_uploaded_file(df):
    """
    Основная функция анализа DataFrame:
    - Проверяет наличие ошибок в данных.
    - Возвращает список ошибок и предполагаемое время обработки.
    """
    errors = []
    errors.extend(check_required_columns(df))
    errors.extend(check_date_format(df))
    errors.extend(check_purchase_amount(df))

    processing_time = estimate_processing_time(len(df))

    if errors:
        return errors, None  # Возвращаем список ошибок и None для времени
    return [], processing_time  # Возвращаем пустой список ошибок и время обработки



def check_required_columns(df):
    """Проверяет наличие всех необходимых столбцов."""
    required_columns = ['customer_name', 'purchase_amount', 'purchase_date']
    errors = []
    for column in required_columns:
        if column not in df.columns:
            errors.append(f"Отсутствует столбец: {column}")
    return errors


def check_date_format(df):
    """Проверяет формат даты в столбце 'purchase_date'."""
    errors = []
    if 'purchase_date' in df.columns:
        try:
            pd.to_datetime(df['purchase_date'])
        except Exception:
            invalid_rows = df[~pd.to_datetime(df['purchase_date'], errors='coerce').notna()]
            for index, row in invalid_rows.iterrows():
                errors.append(f"Некорректный формат даты в строке {index + 1}: {row['purchase_date']}")
    return errors


def check_purchase_amount(df):
    """Проверяет значения в столбце 'purchase_amount'."""
    errors = []
    if 'purchase_amount' in df.columns:
        if not pd.api.types.is_numeric_dtype(df['purchase_amount']):
            errors.append("Некорректный формат чисел в 'purchase_amount'")
        else:
            invalid_rows = df[df['purchase_amount'] < 0]
            for index, row in invalid_rows.iterrows():
                errors.append(
                    f"Отрицательное значение в 'purchase_amount' в строке {index + 1}: {row['purchase_amount']}")
    return errors


def estimate_processing_time(row_count):
    """Определяет предполагаемое время обработки файла."""
    if row_count > 1000:
        return "долгая обработка"
    elif row_count > 100:
        return "среднее время обработки"
    return "быстрая обработка"


@app.route('/rfm_analysis_test', methods=['GET', 'POST'])
def rfm_analysis_test():
    errors = []
    results = None

    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            errors.append("Файл не выбран.")
        else:
            try:
                df = pd.read_csv(file)
                validation_errors, _ = analyze_uploaded_file(df)
                if validation_errors:
                    errors.extend(validation_errors)
                else:
                    results = perform_rfm_analysis(df)
                    if isinstance(results, str):  # Если results — это строка, значит произошла ошибка
                        errors.append(results)
                        results = None
            except Exception as e:
                errors.append(f"Ошибка обработки файла: {e}")

        # Получение параметров сортировки
        sort_by = request.args.get('sort_by', 'RFM_Score')  # По умолчанию сортируем по RFM Score
        order = request.args.get('order', 'desc')  # По умолчанию сортировка по убыванию

        # Пример использования pandas DataFrame для сортировки
        if results is not None and not results.empty:
            ascending = (order == 'asc')  # Преобразуем строку в булево значение
            results = results.sort_values(by=sort_by, ascending=ascending)

    return render_template('rfm_analysis_test.html', errors=errors, results=results)


# def rfm_analysis():
#     errors = []
#     results = {}
#     descriptions = {
#         "111": "Недавние, частые, высокие суммы",
#         "112": "Недавние, частые, средние суммы",
#         "113": "Недавние, частые, низкие суммы",
#         "123": "Недавние, редкие, низкие суммы",
#         "213": "Средние по давности, редкие, низкие суммы",
#         "333": "Давние, редкие, низкие суммы",
#         # Добавьте остальные категории
#     }
#
#     if request.method == 'POST':
#         file = request.files['file']
#         if not file:
#             errors.append("Файл не был загружен.")
#             return render_template('rfm_analysis.html', errors=errors)
#
#         try:
#             df = pd.read_csv(file)
#             validation_errors, processing_time = analyze_uploaded_file(df)  # Разделяем кортеж
#
#             if validation_errors:  # Проверяем только список ошибок
#                 errors.extend(validation_errors)
#             else:
#                 print("RFM Analysis is starting...")  # Для отладки
#                 results = perform_rfm_analysis(df)
#         except Exception as e:
#             errors.append(f"Ошибка обработки файла: {e}")
#
#     return render_template('rfm_analysis.html', errors=errors, results=results, descriptions=descriptions)


def perform_rfm_analysis(df):
    # Проверяем, что DataFrame не пустой
    if df is None or df.empty:
        return "Загруженный файл пуст или отсутствует."

    # Убеждаемся, что данные содержат нужные столбцы
    required_columns = {'customer_name', 'purchase_amount', 'purchase_date'}
    if not required_columns.issubset(df.columns):
        return "Ошибка: файл должен содержать столбцы customer_name, purchase_amount, purchase_date."

    # Преобразуем purchase_date в datetime
    df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
    if df['purchase_date'].isnull().values.any():
        return "Ошибка: неверный формат дат в столбце purchase_date."

    # Удаляем строки с отсутствующими значениями
    df = df.dropna()

    # Используем текущую дату для расчета Recency
    today = pd.Timestamp.now()

    # Вычисляем RFM метрики
    rfm_table = df.groupby('customer_name').agg({
        'purchase_date': lambda x: (today - x.max()).days,  # Recency
        'purchase_amount': 'sum',  # Monetary
        'customer_name': 'count'  # Frequency (количество записей)
    }).rename(columns={
        'purchase_date': 'recency',
        'purchase_amount': 'monetary',
        'customer_name': 'frequency'
    })

    # Вычисляем квартильные пороги
    quantiles = rfm_table.quantile(q=[0.33, 0.66]).to_dict()

    # Функции для классификации на основе квартилей
    def r_class(x):
        if x <= quantiles['recency'][0.33]:
            return 3
        elif x <= quantiles['recency'][0.66]:
            return 2
        else:
            return 1

    def fm_class(x, column):
        if x <= quantiles[column][0.33]:
            return 1
        elif x <= quantiles[column][0.66]:
            return 2
        else:
            return 3

    # Применяем классификацию
    rfm_table['R'] = rfm_table['recency'].apply(r_class)
    rfm_table['F'] = rfm_table['frequency'].apply(fm_class, column='frequency')
    rfm_table['M'] = rfm_table['monetary'].apply(fm_class, column='monetary')

    # Создаем RFM-сегменты
    rfm_table['RFM_Score'] = rfm_table['R'].astype(str) + rfm_table['F'].astype(str) + rfm_table['M'].astype(str)

    return rfm_table.reset_index()


def perform_rfm_analysis_old(df):
    # Проверяем, что DataFrame не пустой
    if df is None or df.empty:
        return "Загруженный файл пуст или отсутствует."

    # Убеждаемся, что данные содержат нужные столбцы
    required_columns = {'customer_name', 'purchase_amount', 'purchase_date'}
    if not required_columns.issubset(df.columns):
        return "Ошибка: файл должен содержать столбцы customer_name, purchase_amount, purchase_date."

    # Преобразуем purchase_date в datetime
    df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
    if df['purchase_date'].isnull().values.any():
        return "Ошибка: неверный формат дат в столбце purchase_date."

    # Вычисляем RFM метрики
    #today = df['purchase_date'].max()


    # Используем текущую дату вместо максимальной даты из набора данных
    today = pd.Timestamp.now()

    # Расчет Recency (давность последней покупки)
    df['recency'] = (today - df['purchase_date']).dt.days


    # Агрегируем данные по каждому клиенту
    agg_dict = {
        'recency': ['min'],
        'purchase_amount': ['sum'],
        'customer_name': ['count']
    }
    grouped_df = df.groupby('customer_name').agg(agg_dict)

    # Переименовываем колонки
    grouped_df.columns = ['recency', 'monetary', 'frequency']

    # Нормализуем значения
    scaler = MinMaxScaler(feature_range=(0, 100))
    grouped_df['normalized_recency'] = scaler.fit_transform(grouped_df[['recency']].values)
    grouped_df['normalized_frequency'] = scaler.fit_transform(grouped_df[['frequency']].values)
    grouped_df['normalized_monetary'] = scaler.fit_transform(grouped_df[['monetary']].values)

    # Вычисляем общий RFM Score
    grouped_df['RFM_Score'] = grouped_df['normalized_recency'] + grouped_df['normalized_frequency'] + grouped_df[
        'normalized_monetary']

    # Сортировка по убыванию RFM Score
    grouped_df.sort_values(by='RFM_Score', ascending=False, inplace=True)

    return grouped_df.reset_index()






def perform_rfm_analysis_old_old(df):
    # Проверяем, что DataFrame не пустой
    if df is None or df.empty:
        return "Загруженный файл пуст или отсутствует."

    # Убеждаемся, что данные содержат нужные столбцы
    required_columns = {'customer_name', 'purchase_amount', 'purchase_date'}
    if not required_columns.issubset(df.columns):
        return "Ошибка: файл должен содержать столбцы customer_name, purchase_amount, purchase_date."

    # Преобразуем purchase_date в datetime
    df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
    if df['purchase_date'].isnull().values.any():
        return "Ошибка: неверный формат дат в столбце purchase_date."

    # Вычисляем RFM метрики
    today = df['purchase_date'].max()

    # Расчет Recency (давность последней покупки)
    df['recency'] = (today - df['purchase_date']).dt.days

    # Расчет Frequency (количество покупок)
    frequency = df.groupby(['customer_name'])['customer_name'].count().reset_index(name='frequency')

    # Расчет Monetary (суммарная стоимость всех покупок)
    monetary = df.groupby(['customer_name'])['purchase_amount'].sum().reset_index(name='monetary')

    # Объединение всех показателей в единый DataFrame
    rfm_df = df.merge(frequency, on='customer_name').merge(monetary, on='customer_name')

    # Нормализация значений Recency, Frequency и Monetary
    scaler = MinMaxScaler(feature_range=(0, 100))
    rfm_df['normalized_recency'] = scaler.fit_transform(rfm_df[['recency']])
    rfm_df['normalized_frequency'] = scaler.fit_transform(rfm_df[['frequency']])
    rfm_df['normalized_monetary'] = scaler.fit_transform(rfm_df[['monetary']])

    # Вычисление общего RFM Score
    rfm_df['RFM_Score'] = rfm_df['normalized_recency'] + rfm_df['normalized_frequency'] + rfm_df['normalized_monetary']

    # Сортировка по убыванию RFM Score
    rfm_df.sort_values(by='RFM_Score', ascending=False, inplace=True)

    return rfm_df

@app.route('/edit_test_db_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_test_db_user(user_id):
    # Проверяем, что текущий пользователь - администратор
    current_user_id = session.get('user_id')
    current_user = User.query.get_or_404(current_user_id)
    if current_user.permission != 1:
        flash("Доступ запрещен!", "danger")
        return redirect('/')

    # Получаем записи TestDB для выбранного пользователя
    test_db_records = TestDB.query.filter_by(user_id=user_id).all()
    selected_user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Обработка добавления новой записи
        customer_name = request.form.get('customer_name')
        purchase_amount = request.form.get('purchase_amount')
        purchase_date = request.form.get('purchase_date')

        new_record = TestDB(
            user_id=user_id,
            customer_name=customer_name,
            purchase_amount=purchase_amount,
            purchase_date=datetime.strptime(purchase_date, '%Y-%m-%d'),
        )
        db.session.add(new_record)
        db.session.commit()
        flash("Новая запись добавлена!", "success")
        return redirect(url_for('edit_test_db_user', user_id=user_id))

    return render_template('edit_test_db_user.html', test_db_records=test_db_records, user=selected_user)








if __name__ == '__main__':
    app.secret_key = SECRET_KEY#'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    with app.app_context():
        db.create_all()#если нет таблиц - создастd
    # sess.init_app(app)

    app.debug = True
    app.run()


