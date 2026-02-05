from config import app, db
from database.store import Storage

def add_products():
    with app.app_context():
        # Проверяем, есть ли уже товары, чтобы не дублировать
        if Storage.query.count() == 5:
            print("Склад уже содержит товары.")
            return

        # Создаем тестовые продукты
        p1 = Storage(name="Картофель", count=50, type_of_product="продукт")
        p2 = Storage(name="Мясо (Говядина)", count=20, type_of_product="продукт")
        p3 = Storage(name="Молоко", count=30, type_of_product="продукт")
        p4 = Storage(name="Лук", count=15, type_of_product="продукт")
        p5 = Storage(name="Пицца Пепперони", count=10, type_of_product="блюдо")
        
        for product in [p1, p2, p3, p4, p5]:
            if not Storage.query.filter_by(name=product.name).first():
                db.session.add(product)
        db.session.commit()
        print("Тестовые товары успешно добавлены на склад!")

if __name__ == "__main__":
    add_products()