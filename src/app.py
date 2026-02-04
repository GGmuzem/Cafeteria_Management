from flask_sqlalchemy import SQLAlchemy
import os, student, cook, service
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from config import app, db, login_manager
from database.users import User
from auth import login_user_db, register_user
from cook import cook_bp 

app.register_blueprint(cook_bp) #блюпринт повара


@login_manager.user_loader #Загрузка пользователя
def load_user(user_id):
    return User.query.get(int(user_id))



def create_db():
    # Получаем путь к базе данных из конфига
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    if uri.startswith('sqlite:///'):
        db_path = uri.replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print(f"Создание базы данных по пути: {db_path}")
            with app.app_context():
                db.create_all()
            print("База данных успешно создана!")
    else:
        with app.app_context():
            db.create_all()

# Загрузка пользователей
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Главная страница
@app.route("/")
def index():
    return render_template("index.html")

# Страница входа в аккаунт
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_data = request.form.get("login")
        password_data = request.form.get("password")

        if login_user_db(login_data, password_data):
            return redirect(url_for("account"))
        else:
            return "Неверный логин или пароль"

    return render_template("login.html")

# Страница регистрации
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login_data = request.form.get("login")
        password_data = request.form.get("password")
        password_repeat = request.form.get("confirm_password")

        user = register_user(login_data, password_data, password_repeat)

        if user:
            login_user(user)
            return redirect(url_for("account"))
        else:
            return "Ошибка регистрации"
    return render_template("register.html")

# Страница профиля
@app.route("/account")
@login_required
def account():
    return render_template("account.html")

@app.route('/logout')
@login_required
def logout():
    logout_user() # Удаляет сессию
    return redirect(url_for('login'))

if __name__ == "__main__":
    create_db()
    app.run(debug=True)

