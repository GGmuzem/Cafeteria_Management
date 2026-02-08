"""
Какие функции для администратора реализуются здесь:

    Просмотр истории заказов и посещаемости
    Просмотр заявок на покупку продуктов и их согласование и изменение ✅
    Экспорт истории заявок и истории заказов
    Изменение роли для пользователя ✅
"""

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from config import db, app
from database.users import User
from database.requests import Requests
from database.history import history_operation

admin_bp = Blueprint("admin", __name__, url_prefix="/admin_requests")


@admin_bp.route("/", methods=["GET", "POST"])
@login_required
def admin_requests():
    edit_id = None
    if current_user.role != "admin": #проверка роли
        return "Доступ запрещён", 403

    if request.method == "POST":
        action = request.form.get("action")

        if action == "start_edit":
            edit_id = int(request.form.get("request_id"))

        if action == "approve_request": #одобрение заявки
            req = Requests.query.get(request.form.get("request_id"))
            if req and req.status == "pending":
                req.status = "approved"
                db.session.commit()

        elif action == "reject_request": #отклонение заявки
            req = Requests.query.get(request.form.get("request_id"))
            if req and req.status == "pending":
                req.status = "rejected"
                db.session.commit()

        elif action == "edit_request":
            req = Requests.query.get(request.form.get("request_id"))
            if req:
                req.product = request.form.get("product")
                req.amount = int(request.form.get("amount"))
                req.status = request.form.get("status")
                db.session.commit()

        elif action == "change_role": #изменение роли пользователю
            user = User.query.get(request.form.get("user_id"))
            if user:
                user.role = request.form.get("role")
                db.session.commit()



    history = history_operation.query.order_by(history_operation.date.desc()).all()
    requests = Requests.query.order_by(Requests.date.desc()).all()
    users = User.query.all()
    requests = Requests.query.all()

    return render_template("admin/index.html", history=history, requests=requests, users=users, edit_id=edit_id)
    #Изменение роли пользователей


@app.route('/admin/history')
@login_required
def admin_history():
    if current_user.role != 'admin':
        return "Доступ запрещен", 403
    
    # Запрос всей истории с присоединением таблицы пользователей для получения логина
    history = db.session.query(history_operation, User).join(User, history_operation.user == User.id).order_by(history_operation.date.desc()).all()
    
    return render_template('admin_history.html', history=history)