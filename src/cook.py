from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from config import db
from database.menu import Menu
from database.store import Storage
from database.requests import Requests
from database.history import History


cook_bp = Blueprint("cook", __name__, url_prefix="/cook")


@cook_bp.route("/", methods=["GET", "POST"])
@login_required
def cook_panel():
    if current_user.role != "cook":
        return "Доступ запрещён", 403

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_menu": #Добавление блюда
            name = request.form.get("name")
            price = request.form.get("price")
            composition_raw = request.form.get("composition")

            if not name or not price or not composition_raw:
                return "Заполните все поля", 400

            composition_list = [
                item.strip()
                for item in composition_raw.split(",")
                if item.strip()
            ]

            dish = Menu(
                name=name,
                price=int(price),
                composition=", ".join(composition_list)
            )

            db.session.add(dish)
            db.session.commit()

            history = History(
                user=current_user.id,
                type_of_transaction="add_menu",
                amount=price,
                date=datetime.now()
            )

            db.session.add(history)
            db.session.commit()

            return redirect(url_for("cook.cook_panel"))


        if action == "create_request": #Создание заявки
            product = request.form.get("product")
            amount = request.form.get("amount")

            new_request = Requests(
                user=current_user.id,
                product=product,
                amount=int(amount),
                status="pending",
                date=datetime.now()
            )

            db.session.add(new_request)
            db.session.commit()

            history = History(
                user=current_user.id,
                type_of_transaction="create_request",
                amount=amount,
                date=datetime.now()
            )

            db.session.add(history)
            db.session.commit()

            return redirect(url_for("cook.cook_panel"))

    menu = Menu.query.all()
    storage = Storage.query.all()
    history = History.query.order_by(History.date.desc()).all()

    return render_template(
        "cook/index.html",
        menu=menu,
        storage=storage,
        history=history
    )