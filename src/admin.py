"""
Какие функции для администратора реализуются здесь:

    Просмотр истории заказов и посещаемости
    Просмотр заявок на покупку продуктов и их согласование и изменение
    Экспорт истории заявок и истории заказов
    Изменение роли для пользователя 
"""

from flask import Blueprint, render_template, request, redirect, url_for, Response
from flask_login import login_required, current_user
import csv
import io
from config import db
from database.users import User
from database.history import History
from database.requests import Requests

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/", methods=["GET", "POST"])
@login_required
def admin_panel():
    if current_user.role != "admin": #проверка роли
        return "Доступ запрещён", 403

    if request.method == "POST":
        action = request.form.get("action")

        if action == "approve_request": #одобрение заявки
            req = Requests.query.get(request.form.get("request_id"))
            if req:
                req.status = "approved"
                db.session.commit()

        elif action == "reject_request": #отклонение заявки
            req = Requests.query.get(request.form.get("request_id"))
            if req:
                req.status = "rejected"
                db.session.commit()

        elif action == "change_role": #изменение роли пользователю
            user = User.query.get(request.form.get("user_id"))
            if user:
                user.role = request.form.get("role")
                db.session.commit()

        return redirect(url_for("admin.admin_panel"))

    history = History.query.order_by(History.date.desc()).all()
    requests = Requests.query.order_by(Requests.date.desc()).all()
    users = User.query.all()

    return render_template(
        "admin/index.html",
        history=history,
        requests=requests,
        users=users
    )
