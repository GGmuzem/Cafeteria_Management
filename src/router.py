"""
Какие функции реализуются здесь:

    Принимает запросы: (создать заказ) или (получить список заказов для повара).
    Вызывает логику: Он не считает деньги и не проверяет продукты сам, он передает эту задачу в service.py.
    Возвращает ответ: Отдает данные обратно на фронтенд в формате, описанном в schemas.py.
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from src.student import StudentService
from src.schemas import StudentSchema
from src.database.users import User
from src.config import db
from src.database.history import History
from src.database.store import Storage


current_dir = os.path.dirname(os.path.abspath(__file__)) # Папка src
root_dir = os.path.dirname(current_dir) # Корневая папка проекта
template_dir = os.path.join(root_dir, 'frontend', 'templates') # Путь к frontend/templates
# Создаем чертеж для путей, связанных с кошельком
wallet_bp = Blueprint('wallet_bp', __name__, template_folder=template_dir)
@wallet_bp.route("/wallet", methods=["GET", "POST"])
@login_required
def wallet_page():
    user = current_user
    
    message = None
    message_type = None
    """
    Страница кошелька.
    GET запрос: Просто показывает страницу с балансом.
    POST запрос: Обрабатывает нажатие кнопок Пополнить/Снять.
    """
    
    # --- 1. ЕСЛИ ПРИШЛИ ДАННЫЕ ОТ ПОЛЬЗОВАТЕЛЯ (POST) ---
    if request.method == "POST":
        # Получаем данные из формы
        action = request.form.get("action")   # deposit или withdraw
        amount_str = request.form.get("amount") # Сумма строкой

        #1: ВАЛИДАЦИЯ (Schema)
        # Узнаём корректность данных от пользователя
        amount, errors = StudentSchema.validate_payment(amount_str)

        if errors:
            # если ошибка
            message = errors[0] # Берем текст ошибки из схемы
            message_type = "error"
        else:
            # если всё ок
            if action == "deposit":
                success, msg = StudentService.top_up_balance(user, amount)
            elif action == "withdraw":
                success, msg = StudentService.withdraw_balance(user, amount)
            
            message = msg
            # Если операция прошла успешно — зеленый цвет, если нет денег — красный
            message_type = "success" if success else "error"

    # 2. Если просто зашли на страницу (GET)
    # Запрашиваем актуальные данные, чтобы показать пользователю
    balance, card_last_4 = StudentService.get_wallet_info(user)
    
    history_records = History.query.filter_by(user=user.id).order_by(History.date.desc()).all()#запрос истории 

    # Отдаем HTML и вставляем туда цифры
    return render_template("student/history.html",
                         balance=balance, 
                         card_number=card_last_4,
                         message=message,
                         message_type=message_type,
                         history=history_records)

@wallet_bp.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory_page():
    """
    Страница склада.
    Показывает товары и позволяет добавлять новые (если админ/повар).
    """
    # 1. Добавление товара
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        category = request.form.get('category')

        # Проверка, что поля заполнены
        if name and quantity and price:
            try:
                new_item = Storage(
                    name=name, 
                    quantity=int(quantity), 
                    price=int(price),
                    category=category
                )
                db.session.add(new_item)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Ошибка добавления товара: {e}")
        
        # Перезагружаем страницу, чтобы сбросить форму
        return redirect(url_for('wallet_bp.inventory_page'))

    # 2. Отображение списка
    items = Storage.query.all()
    

    return render_template('cook/inventory.html', items=items)


@wallet_bp.route('/inventory/delete/<int:item_id>')
@login_required
def delete_inventory_item(item_id):
    """
    Удаление товара по ID
    """
    item = Storage.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    
    return redirect(url_for('wallet_bp.inventory_page'))