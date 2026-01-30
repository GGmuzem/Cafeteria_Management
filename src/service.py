"""
Какие функции реализуются здесь: (самое сложное)
    Проверка условий: Хватает ли у студента денег на балансе? Есть ли продукты на складе для этого блюда?
    Транзакции: Списать деньги с кошелька, создать запись о заказе, уменьшить количество продуктов на складе.
"""


from database.store import Storage
from config import db
from schemas import StorageCreate, StorageDelete
from pydantic import ValidationError

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