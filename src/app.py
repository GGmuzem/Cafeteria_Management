from flask_sqlalchemy import SQLAlchemy
import os, student, cook, service, admin
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
import os
from flask import request, redirect, url_for, Flask, render_template, flash
from config import app, db, login_manager
from werkzeug.security import generate_password_hash
from database.users import User
from database.notifications import Notification
from auth import login_user_db, register_user
from cook import cook_bp 
from service import buy_food_service
from database.history import history_operation
from database.wallets import Wallet


app.register_blueprint(cook_bp) #блюпринт повара


@login_manager.user_loader #Загрузка пользователя
def load_user(user_id):
    return User.query.get(int(user_id))
from flask_login import logout_user, login_user, login_required, current_user
from functools import wraps


def create_db():
    # Получаем путь к базе данных из конфига
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    if uri.startswith('sqlite:///'):
        db_path = uri.replace('sqlite:///', '')

        if not os.path.exists(db_path):
            print(f"Creating database at: {db_path}")
            with app.app_context():
                db.create_all()
            print("Database successfully created!")
    else:
        with app.app_context():
            db.create_all()

    # Создаем админа по умолчанию если его нет (проверяем всегда)
    with app.app_context():
        # Убедимся, что таблицы существуют (если файл был, но таблицы не созданы)
        db.create_all()
        
        existing_admin = User.query.filter_by(login="admin").first()
        if not existing_admin:
            print("Creating default admin user...")
            hashed_password = generate_password_hash("admin", method='pbkdf2:sha256')
            new_admin = User(login="admin", password=hashed_password, role="admin", wallet=None)
            db.session.add(new_admin)
            db.session.commit()
            print("Admin created: login=admin, password=admin")

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

        return "Неверный логин или пароль"

    return render_template("auth/login.html")


# Страница регистрации
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login_data = request.form.get("login")
        password_data = request.form.get("password")
        password_repeat = request.form.get("confirm_password")

        user, error_message = register_user(login_data, password_data, password_repeat)
        if user:
            return redirect(url_for("account"))
        
        flash(error_message)
        return render_template("auth/register.html")
    return render_template("auth/register.html")

@app.route("/account", methods=["GET", "POST"])

# Страница профиля
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    # Создание таблицы history_operation
    from sqlalchemy import inspect
    with app.app_context():
        inspector = inspect(db.engine)
        if 'history_operation' not in inspector.get_table_names():
            history_operation.__table__.create(db.engine)

    if request.method == "POST":
        how_many_on = request.form.get("how_many_on")
        how_many_off = request.form.get("how_many_off")
        if how_many_on:
            try:
                current_user.add_money(float(how_many_on))
            except:
                pass
        if how_many_off:
            try:
                current_user.rem_money(float(how_many_off))
            except:
                pass

        if "email" in request.form:
            current_user.email = request.form.get("email")
        if "allergen" in request.form:
            current_user.allergen = request.form.get("allergen")
        if "preferences" in request.form:
            current_user.preferences = request.form.get("preferences")
        
        db.session.commit()
        return redirect(url_for("account"))

    return render_template(
        "auth/account.html",
        user=current_user,
        wallet=current_user.get_wallet()
    )


# Страница истории операций с балансом
@app.route("/history_operation")
@login_required
def history_operation():
    his = current_user.get_history_operation()
    return render_template("history_operation.html", history=his)


# Страница покупки(переход обратно в меню)
@app.route("/buy_food/<int:food_id>")
@login_required
def buy_food(food_id):
    success = buy_food_service(current_user.id, food_id)
    return redirect(url_for("menu"))


@app.route('/logout')
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
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




    logout_user()  # Удаляет сессию
    return redirect(url_for('login'))


if __name__ == "__main__":
    create_db()
    app.run(debug=True)
