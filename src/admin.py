"""
Какие функции для администратора реализуются здесь:

    Просмотр истории заказов и посещаемости
    Просмотр заявок на покупку продуктов и их согласование и изменение
    Экспорт истории заявок и истории заказов
    Изменение роли пользователей
"""
from flask import render_template
from config import app, db
from flask_login import login_required, current_user
from database.history import history_operation
from database.users import User

@app.route('/admin/history')
@login_required
def admin_history():
    if current_user.role != 'admin':
        return "Доступ запрещен", 403
    
    # Запрос всей истории с присоединением таблицы пользователей для получения логина
    history = db.session.query(history_operation, User).join(User, history_operation.user == User.id).order_by(history_operation.date.desc()).all()
    
    return render_template('admin_history.html', history=history)