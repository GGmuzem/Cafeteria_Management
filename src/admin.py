"""
Какие функции для администратора реализуются здесь:

    Просмотр истории заказов и посещаемости
    Просмотр заявок на покупку продуктов и их согласование и изменение ✅
    Экспорт истории заявок и истории заказов
    Изменение роли для пользователя ✅
"""

from flask import Blueprint, render_template, request, send_file
from flask_login import login_required, current_user
from config import db, app
from database.users import User
from database.requests import Requests
from database.history import history_operation
import io
import csv
from datetime import datetime

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
                try:
                    req.price_per_unit = int(request.form.get("price_per_unit"))
                except (ValueError, TypeError):
                    pass # Ignore if invalid or missing
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


@admin_bp.route("/user/<int:user_id>")
@login_required
def user_profile(user_id):
    if current_user.role != "admin":
        return "Доступ запрещён", 403
    
    user = User.query.get(user_id)
    if not user:
        return "Пользователь не найден", 404
        
    return render_template("admin/user_profile.html", user=user)


@app.route('/admin/stats')
@login_required
def admin_stats():
    if current_user.role != 'admin':
        return "Доступ запрещен", 403
    
    from datetime import datetime, timedelta
    
    # Запрос всей истории с присоединением таблицы пользователей для получения логина
    history = db.session.query(history_operation, User).join(User, history_operation.user == User.id).order_by(history_operation.date.desc()).all()
    
    # Статистика посещаемости (уникальные пользователи, купившие еду)
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(weeks=1)
    month_ago = now - timedelta(days=30)
    
    def get_unique_visitors(since_date):
        return db.session.query(history_operation.user).filter(
            history_operation.date >= since_date,
            history_operation.type_of_transaction.in_(['Завтрак', 'Обед'])
        ).distinct().count()

    stats = {
        'day': get_unique_visitors(day_ago),
        'week': get_unique_visitors(week_ago),
        'month': get_unique_visitors(month_ago)
    }
    
    return render_template('admin_history.html', history=history, stats=stats)


@admin_bp.route("/export_stats_csv")
@login_required
def export_stats_csv():
    if current_user.role != "admin":
        return "Доступ запрещён", 403

    import io
    import csv
    from flask import send_file
    from datetime import datetime

    # Создаем буфер в памяти
    proxy = io.StringIO()
    writer = csv.writer(proxy, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Заголовки
    headers = ["ID", "Пользователь", "Роль", "Тип операции", "Сумма", "Дата и время"]
    writer.writerow(headers)

    # Получаем данные
    history = db.session.query(history_operation, User).join(User, history_operation.user == User.id).order_by(history_operation.date.desc()).all()

    for record, user in history:
        writer.writerow([
            record.id,
            user.login,
            user.role,
            record.type_of_transaction,
            record.amount,
            record.date.strftime('%d.%m.%Y %H:%M')
        ])

    # Создаем байтовый поток из строкового
    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode('utf-8-sig')) # BOM для корректного открытия в Excel
    mem.seek(0)
    proxy.close()

    return send_file(
        mem,
        as_attachment=True,
        download_name=f"history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mimetype="text/csv"
    )