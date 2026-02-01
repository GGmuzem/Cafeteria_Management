"""
Какие функции реализуются здесь:

    Пополнение кошелька через yookassa
    Создание отзывов к каждому блюду
    Изменение профиля (аллергии, предпочтения, изменение пароля, изменение почты)
    Оплата абонемента
    Просмотр истории заказов и пополнения кошелька
    
"""
from flask import render_template, request
from config import app, db
from flask_login import login_required
from database.users import User
from database.menu import Menu

@app.route('/menu')
@login_required
def menu():
    allergen = request.args.get('allergen')
    menu_items = Menu.query.all()

    # Если указан аллерген, фильтруем список
    if allergen:
        allergen = allergen.lower().strip()
        # Оставляем только те блюда, в ингредиентах которых НЕТ указанного аллергена
        menu_items = [
            item for item in menu_items
            if not any(allergen in str(ing).lower() for ing in item.composition.get('ingredients', []))
        ]

    return render_template('menu.html', menu_items=menu_items)
