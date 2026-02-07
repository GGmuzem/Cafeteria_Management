"""
Какие функции реализуются здесь:

    Пополнение кошелька через yookassa
    Создание отзывов к каждому блюду
    Изменение профиля (аллергии, предпочтения, изменение пароля, изменение почты)
    Оплата абонемента
    Просмотр истории заказов и пополнения кошелька
    
"""
from flask import render_template, request, redirect, url_for, flash
from config import app, db
from flask_login import login_required
from database.users import User
from database.reviews import Reviews
from datetime import datetime
from flask_login import current_user
from database.menu import Menu
from service import buy_food_service

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

@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    
    if current_user.role == "student":
        return "Доступ запрещен", 403
    
    student_login = request.args.get('student_login')
    target_user = None
    balance = 0

    if student_login:
        target_user = User.query.filter_by(login=student_login).first()
        if target_user:
            balance = target_user.get_balance()
        else:
            flash(f"Ученик с логином '{student_login}' не найден")
    
    # Фильтрация по типу (Завтрак/Обед)
    meal_type = request.args.get('meal_type')
    query = Menu.query
    if meal_type:
        query = query.filter_by(meal_type=meal_type)
    
    menu_items = query.all()
    
    items_data = []
    # Получаем список аллергенов пользователя
    if target_user:
        user_allergens = [a.strip().lower() for a in (target_user.allergen or "").split(',') if a.strip()]
    else:
        user_allergens = []
    
    for item in menu_items:
        is_suitable = True
        warning = None
        
        # Получаем состав блюда в виде строки для поиска
        if isinstance(item.composition, dict):
            ingredients = item.composition.get('ingredients', [])
            ing_str = ", ".join(ingredients).lower() if isinstance(ingredients, list) else str(ingredients).lower()
        else:
            ing_str = str(item.composition).lower()
            
        # Проверяем совпадения с аллергенами
        for allergen in user_allergens:
            if allergen in ing_str:
                is_suitable = False
                warning = f"Содержит аллерген: {allergen}"
                break
        
        items_data.append({
            'obj': item,
            'is_suitable': is_suitable,
            'warning': warning
        })

    if request.method == 'POST':
        student_login_post = request.form.get('student_login')
        target_user_post = User.query.filter_by(login=student_login_post).first()
        
        if not target_user_post:
            flash("Ошибка: Ученик не выбран или не найден.")
            return redirect(url_for('order', meal_type=meal_type))

        food_ids = request.form.getlist('food_ids')
        if not food_ids:
            flash("Вы не выбрали ни одного блюда.")
            return redirect(url_for('order', meal_type=meal_type, student_login=student_login_post))
            
        success_count = 0
        fail_count = 0
        
        for fid in food_ids:
            if buy_food_service(target_user_post.id, int(fid)):
                success_count += 1
            else:
                fail_count += 1
        
        flash(f"Заказано: {success_count}. Ошибок (недостаточно средств или лимит на 1 порцию): {fail_count}.")
        return redirect(url_for('order', meal_type=meal_type, student_login=student_login_post))

    return render_template('order.html', balance=balance, items=items_data, current_meal_type=meal_type, target_user=target_user)