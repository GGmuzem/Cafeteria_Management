from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from config import db
from database.menu import Menu
from database.store import Storage
from database.requests import Requests
from database.history import history_operation as History
from datetime import datetime


cook_bp = Blueprint("cook", __name__, url_prefix="/cook_panel")


@cook_bp.route("/", methods=["GET", "POST"])
@login_required
def cook_panel():
    if current_user.role == "student":
        return "Доступ запрещён", 403
    edit_menu = None
    edit_menu_id = request.args.get("edit_menu_id", type=int)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "start_edit_menu":
            edit_menu_id = int(request.form.get("menu_id"))
            edit_menu = Menu.query.get(edit_menu_id)
        
        elif action == "save_menu":
            menu_id = int(request.form.get("menu_id"))
            dish = Menu.query.get(menu_id)
            if not dish:
                return "Блюдо не найдено", 404
            
            name = request.form.get("name", "").strip()
            price_str = request.form.get("price", "").strip()
            composition = request.form.get("composition", "").strip()
            weight_str = request.form.get("weight", "").strip()
            meal_type = request.form.get("meal_type", "").strip()

            if not name or not price_str or not composition or not meal_type:
                return "Заполните все поля", 400
            
            try:
                price = int(price_str)
                weight = int(weight_str)
            except ValueError:
                return "Цена должна быть числом", 400

            dish.name = name
            dish.price = price
            dish.composition = composition
            dish.weight = weight
            dish.meal_type = meal_type

            db.session.commit()
            return redirect(url_for("cook.cook_panel"))
        
        elif action == "delete_menu":
            menu_id = request.form.get("menu_id")
            dish = Menu.query.get(menu_id)

            db.session.delete(dish)
            db.session.commit()
            return redirect(url_for("cook.cook_panel"))

        if action == "add_menu": #Добавление блюда
            name = request.form.get("name") #название блюда
            price_str = request.form.get("price") #цена блюда
            composition_raw = request.form.get("composition") #состав блюда
            weight_str = request.form.get("weight", "").strip()
            meal_type = request.form.get("meal_type").strip()

            try:
                price = int(price_str)
                weight = int(weight_str) if weight_str else None  # None, если не указано
            except ValueError:
                return "Цена и вес должны быть числами", 400

            if not name or not price or not composition_raw or not meal_type: #проверка на заполненность всех полей (блюдо, цена, состав, тип)
                return "Заполните все поля", 400

            composition_list = [ #разбивает поле состава по запятым (морковь, рис, греча) -> (морковь рис греча) в бд
                item.strip()
                for item in composition_raw.split(",")
                if item.strip()
            ]

            composition_data = {
                "ingredients": composition_list,
                "weight": weight
            }

            dish = Menu( #создание нового блюда в меню
                name=name, #название блюда
                price=price, #цена блюда
                composition=", ".join(composition_list), #состав блюда
                weight=weight, #вес блюда
                meal_type=meal_type
            )

            db.session.add(dish) #выделение в бд места под новое блюдо
            db.session.commit() #сохранение в бд
            return redirect(url_for("cook.cook_panel"))


        if action == "create_request": #Создание заявки
            product = request.form.get("product")
            amount = request.form.get("amount")
            price_per_unit = request.form.get("price_per_unit")

            new_request = Requests( #данные пользователя по заявке
                user=current_user.id,
                product=product,
                amount=int(amount),
                status="pending", #повар отправляет заяву и ей даётся статус "ожидание"
                date=datetime.now(),
                price_per_unit=int(price_per_unit) if price_per_unit else 0
            )

            db.session.add(new_request) #выделение в бд места под новую заяву
            db.session.commit() #сохранение заявки в бд
            return redirect(url_for("cook.cook_panel"))

    menu = Menu.query.all()
    storage = Storage.query.all()
    history = History.query.order_by(History.date.desc()).all()
    my_requests = Requests.query.filter_by(user=current_user.id).order_by(Requests.date.desc()).all()

    return render_template("cook/index.html", menu=menu, edit_menu=edit_menu, edit_menu_id=edit_menu_id, storage=storage, history=history, my_requests=my_requests)
@cook_bp.route("/edit_menu/<int:id>", methods=["GET", "POST"])
@login_required
def edit_menu(id):
    if current_user.role not in ["cook", "admin"]:
        return "Доступ запрещён", 403
    
    dish = db.session.get(Menu, id)
    if not dish:
        return "Блюдо не найдено", 404

    if request.method == "POST":
        dish.name = request.form.get("name")
        dish.price = int(request.form.get("price"))
        
        # Сохраняем состав в правильном JSON формате
        composition_raw = request.form.get("composition")
        composition_list = [x.strip() for x in composition_raw.split(",") if x.strip()]
        
        dish.composition = {
            "ingredients": composition_list,
            "weight": request.form.get("weight", "")
        }
        
        db.session.commit()
        return redirect(url_for("menu"))

    return render_template("edit_menu.html", dish=dish)

@cook_bp.route("/delete_menu/<int:id>")
@login_required
def delete_menu(id):
    if current_user.role not in ["cook", "admin"]:
        return "Доступ запрещён", 403
        
    dish = db.session.get(Menu, id)
    if dish:
        db.session.delete(dish)
        db.session.commit()
    return redirect(url_for("menu"))