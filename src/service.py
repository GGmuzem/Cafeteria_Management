"""
Какие функции реализуются здесь: (самое сложное)
    Проверка условий: Хватает ли у студента денег на балансе? Есть ли продукты на складе для этого блюда?
    Транзакции: Списать деньги с кошелька, создать запись о заказе, уменьшить количество продуктов на складе.
"""


from database.store import Storage
from config import db
from database.users import User
from database.wallets import Wallet
from database.notifications import Notification
from schemas import StorageCreate, StorageDelete
from pydantic import ValidationError
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash
from config import app, db
from flask_login import login_required, current_user

@app.route('/storage', methods=['GET', 'POST'])
@login_required
def storage():
    if current_user.role == "student":
        return "Доступ запрещен", 403

    # Логика добавления товара (только для админа)
    if request.method == 'POST':
        if current_user.role != 'admin':
            flash("Только администратор может добавлять товары.")
            return redirect(url_for('storage'))
        
        name = request.form.get('name')
        count = request.form.get('count')
        type_of_product = request.form.get('type_of_product')

        try:
            # Формируем данные для функции добавления
            data = {
                "name": name,
                "count": int(count) if count else 0,
                "type_of_product": type_of_product
            }
            result = add_product(data) # Используем существующую функцию
            flash(result)
        except ValueError:
            flash("Ошибка: Количество должно быть числом.")
        
        return redirect(url_for('storage'))

    storage_items = Storage.query.all()
    return render_template('storage.html', storage_items=storage_items)

def add_product(data: dict):
    try:
        validated_data = StorageCreate(**data)
        
        new_item = Storage(
            name=validated_data.name,
            count=validated_data.count,
            type_of_product=validated_data.type_of_product
        )
        db.session.add(new_item)
        db.session.commit()
        return "Товар успешно добавлен"

    except ValidationError as e:
        return f"Ошибка валидации: {e}"

def delete_product(data: dict):
    try:
        validated_data = StorageDelete(**data)
        item = Storage.query.filter_by(name=validated_data.name).first()
        if not item:
            return 'Товар не найден'
        db.session.delete(item)
        db.session.commit()
        return 'Товар успешно удален'
    except ValidationError as e:
        return f"Ошибка валидации: {e}"

@app.route('/storage/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_storage_item(id):
    if current_user.role != 'admin':
        return "Доступ запрещен", 403
    
    item = db.session.get(Storage, id)
    if not item:
        return "Товар не найден", 404

    if request.method == 'POST':
        item.name = request.form.get('name')
        try:
            item.count = int(request.form.get('count'))
        except ValueError:
            flash("Количество должно быть числом")
            return render_template('edit_storage.html', item=item)
            
        item.type_of_product = request.form.get('type_of_product')
        db.session.commit()
        flash("Товар успешно обновлен")
        return redirect(url_for('storage'))

    return render_template('edit_storage.html', item=item)

@app.route('/storage/delete/<int:id>')
@login_required
def delete_storage_item(id):
    if current_user.role != 'admin':
        flash("Только админ может удалять товары")
        return redirect(url_for('storage'))
        
    item = db.session.get(Storage, id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Товар удален")
    else:
        flash("Товар не найден")
    return redirect(url_for('storage'))

def decrease_stock(product_id: int, amount: int = 1):
    """
    Функция для списания 1 единицы (или amount) товара со склада.
    Включает проверки на существование и наличие достаточного количества.
    """
    item = Storage.query.filter_by(id=product_id).first()
    if not item:
        return False, f"Товар '{product_id}' не найден на складе"
    if item.count < amount:
        return False, f"Недостаточно товара '{product_id}' (в наличии: {item.count})"
    item.count -= amount
    db.session.commit()
    
    return True, "Успешно списано"

def send_balance_notification(user_id: int, amount: int, description: str = "Транзакция"):
    """
    Создает уведомление о транзакции.
    """
    user = db.session.get(User, user_id)
    if not user:
        return False, "Пользователь не найден"

    # Ищем кошелек по зашифрованному номеру (связь через user.wallet)
    wallet = db.session.get(Wallet, user.wallet)
    current_balance = wallet.money if wallet else 0
    
    # Создаем уведомление
    if user.email:
        action_type = "Пополнение" if amount > 0 else "Списание"
        message = f"{action_type} на сумму {abs(amount)} руб. {description}. Текущий баланс: {current_balance} руб."
        
        notification = Notification(
            email=user.email,
            subject=f"Баланс: {action_type}",
            message=message
        )
        db.session.add(notification)

    db.session.commit()
    return True, "Уведомление создано"
from config import db
from database.users import User
from database.menu import Menu
from database.store import Storage
from database.history import history_operation
import json

def buy_food_service(user_id, food_id):  # покупка еды
    try:
        user = User.query.get(user_id)
        food = Menu.query.get(food_id)
        
        # Проверка: можно заказать только один Завтрак и один Обед в день
        if food.meal_type in ['Завтрак', 'Обед']:
            start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            existing_order = history_operation.query.filter(
                history_operation.user == user.id,
                history_operation.type_of_transaction == food.meal_type,
                history_operation.date >= start_of_day
            ).first()
            if existing_order:
                return False

        user_balance = user.get_balance()

        if user_balance < food.price:
            return False

        success = user.rem_money(food.price)
        if not success:
            return False

        his = history_operation(
            user=user.id,
            type_of_transaction=food.meal_type,
            amount=food.price
        )

        db.session.add(his)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        return False
