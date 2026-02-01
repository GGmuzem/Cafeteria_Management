from config import app, db
from database.menu import Menu

def add_dish():
    with app.app_context():
        # Создаем объект блюда (название, цена, описание)
        dish = Menu(
            name="Пицца Пепперони",
            price=350,
            composition={"ingredients": ["пепперони", "сыр моцарелла", "тесто"], "weight": 400}
        )
        
        db.session.add(dish)
        db.session.commit()
        print(f"Блюдо '{dish.name}' успешно добавлено в базу данных!")

if __name__ == "__main__":
    add_dish()