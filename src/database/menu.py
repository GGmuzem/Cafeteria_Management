from config import db
# Здесь мы инициализируем и проверяем таблицу menu
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # Здесь храним состав блюда в виде документа (JSON)
    # Например: {"meat": "beef", "weight": 200, "sauce": "bbq"}
    composition = db.Column(db.JSON, nullable=False)
    meal_type = db.Column(db.String(20), nullable=True) # используется в меню завтрак/обед

    
    def __init__(self, name, price, composition, meal_type):
        self.name = name
        self.price = price
        self.composition = composition
        self.meal_type = meal_type


    def __repr__(self):
        return f'<Menu {self.id}>'
