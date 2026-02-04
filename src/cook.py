from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from config import db
from database.menu import Menu
from database.store import Storage
from database.requests import Requests
from database.history import History


cook_bp = Blueprint("cook", __name__, url_prefix="/cook_panel")


@cook_bp.route("/", methods=["GET", "POST"])
@login_required
def cook_panel():
    if current_user.role.lower() not in ("cook", "admin"):
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

            if not name or not price_str or not composition:
                return "Заполните все поля", 400
            
            try:
                price = int(price_str)
            except ValueError:
                return "Цена должна быть числом", 400

            dish.name = name
            dish.price = price
            dish.composition = composition

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
            price = request.form.get("price") #цена блюда
            composition_raw = request.form.get("composition") #состав блюда

            if not name or not price or not composition_raw: #проверка на заполненность всех полей (блюдо, цена, состав)
                return "Заполните все поля", 400

            composition_list = [ #разбивает поле состава по запятым (морковь, рис, греча) -> (морковь рис греча) в бд
                item.strip()
                for item in composition_raw.split(",")
                if item.strip()
            ]

            dish = Menu( #создание нового блюда в меню
                name=name, #название блюда
                price=int(price), #цена блюда
                composition=", ".join(composition_list) #состав блюда
            )

            db.session.add(dish) #выделение в бд места под новое блюдо
            db.session.commit() #сохранение в бд
            return redirect(url_for("cook.cook_panel"))


        if action == "create_request": #Создание заявки
            product = request.form.get("product")
            amount = request.form.get("amount")

            new_request = Requests( #данные пользователя по заявке
                user=current_user.id,
                product=product,
                amount=int(amount),
                status="pending", #повар отправляет заяву и ей даётся статус "ожидание"
                date=datetime.now()
            )

            db.session.add(new_request) #выделение в бд места под новую заяву
            db.session.commit() #сохранение заявки в бд
            return redirect(url_for("cook.cook_panel"))

    menu = Menu.query.all()
    storage = Storage.query.all()
    history = History.query.order_by(History.date.desc()).all()
    my_requests = Requests.query.filter_by(user=current_user.id).order_by(Requests.date.desc()).all()

    return render_template("cook/index.html", menu=menu, edit_menu=edit_menu, edit_menu_id=edit_menu_id, storage=storage, history=history, my_requests=my_requests)