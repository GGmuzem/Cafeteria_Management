from flask_sqlalchemy import SQLAlchemy
import os
from flask import request, redirect, url_for, Flask, render_template, flash
from config import app, db, login_manager
from werkzeug.security import generate_password_hash
from database.users import User
from database.wallets import Wallet
from database.history import History
from database.menu import Menu
from database.store import Storage
from database.reviews import Reviews
from database.requests import Requests
from auth import login_user_db, register_user
from flask_login import logout_user, login_user, login_required, current_user
from functools import wraps


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

# Декоратор для проверки прав доступа к страницам администратора
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("У вас нет прав доступа к этой странице.")
            return redirect(url_for('account'))
        return f(*args, **kwargs)
    return decorated_function

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

@app.route("/admin-panel")
@login_required
@admin_required
def admin_panel():
    users = db.session.query(User, Wallet).outerjoin(Wallet, User.wallet == Wallet.wallet_number).all()
    return render_template("admin_panel.html", users=users)



@app.route("/admin-panel/update_role", methods=["POST"])
@login_required
@admin_required
def admin_update_role():
    user_id = request.form.get("user_id")
    new_role = request.form.get("new_role")
    
    user = User.query.get(user_id)
    if user:
        user.role = new_role
        db.session.commit()
        flash("Роль обновлена")
    else:
        flash("Пользователь не найден")
        
    return redirect(url_for("admin_panel"))

@app.route("/admin-panel/delete_user", methods=["POST"])
@login_required
@admin_required
def admin_delete_user():
    user_id = request.form.get("user_id")
    
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("Пользователь удален")
    else:
        flash("Пользователь не найден")
        
    return redirect(url_for("admin_panel"))

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
    

