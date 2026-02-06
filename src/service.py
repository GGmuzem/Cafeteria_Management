"""
Какие функции реализуются здесь: (самое сложное)
    Проверка условий: Хватает ли у студента денег на балансе? Есть ли продукты на складе для этого блюда?
    Транзакции: Списать деньги с кошелька, создать запись о заказе, уменьшить количество продуктов на складе.
"""

from config import db
from database.users import User
from database.menu import Menu
from database.store import Storage
from database.history import history_operation
import json


def check_food(food):  # хватает ли ингредиентов для блюда
    try:
        if isinstance(food.composition, str):
            comp = json.loads(food.composition)
        else:
            comp = food.composition

        for ingr, need in comp.items():
            item = Storage.query.filter_by(name=ingr).first()
            if not item or item.count < need:
                return False
        return True
    except:
        return False


def buy_food_service(user_id, food_id):  # покупка еды
    try:
        user = User.query.get(user_id)
        food = Menu.query.get(food_id)
        user_balance = user.get_balance()

        if user_balance < food.price:
            return False

        success = user.rem_money(food.price)
        if not success:
            return False

        his = history_operation(
            user_id=user_id,
            operation_type='Покупка',
            how_many=food.price
        )

        db.session.add(his)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        return False