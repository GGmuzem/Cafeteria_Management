from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, current_user, logout_user
from config import app, db, login_manager
from database.users import User
from auth import login_user_db, register_user
from cook import cook_bp 

app.register_blueprint(cook_bp) #блюпринт повара


@login_manager.user_loader #Загрузка пользователя
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route("/") #Главная
def index():
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"]) #Логин
def login():
    if request.method == "POST":
        login_data = request.form.get("login")
        password_data = request.form.get("password")

        if login_user_db(login_data, password_data):
            return redirect(url_for("account"))

        return "Неверный логин или пароль"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"]) #Регистрация
def register():
    if request.method == "POST":
        login_data = request.form.get("login")
        password_data = request.form.get("password")
        password_repeat = request.form.get("confirm_password")

        user = register_user(login_data, password_data, password_repeat)
        if user:
            return redirect(url_for("account"))
        return "Ошибка регистрации"
    return render_template("register.html")


@app.route("/account") #Профиль
@login_required
def account():
    return render_template(
        "account.html",
        user=current_user,
        wallet=current_user.get_wallet()
    )

@app.route("/logout") #Выход
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
