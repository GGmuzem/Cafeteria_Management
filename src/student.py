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
from database.reviews import Reviews
from datetime import datetime
from flask_login import current_user
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
        filtered_items = []
        for item in menu_items:
            # Безопасное получение строки ингредиентов
            if isinstance(item.composition, dict):
                ingredients = item.composition.get('ingredients', [])
                ing_str = ", ".join(ingredients) if isinstance(ingredients, list) else str(ingredients)
            else:
                ing_str = str(item.composition)
            
            if allergen not in ing_str.lower():
                filtered_items.append(item)
        menu_items = filtered_items

    return render_template('menu.html', menu_items=menu_items)

@app.route('/menu/<int:menu_id>/reviews', methods=['GET', 'POST'])
@login_required
def menu_reviews(menu_id):
    menu_item = Menu.query.get_or_404(menu_id)
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        # Простейшая валидация
        if rating and comment:
            new_review = Reviews(
                user=current_user.login,
                review=comment,
                rating=int(rating),
                date=datetime.now(),
                menu_id=menu_id
            )
            db.session.add(new_review)
            db.session.commit()
            
    # Получаем отзывы для этого блюда
    reviews = Reviews.query.filter_by(menu_id=menu_id).order_by(Reviews.date.desc()).all()
    
    return render_template('reviews.html', menu_item=menu_item, reviews=reviews)