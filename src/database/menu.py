from config import db
# Здесь мы инициализируем и проверяем таблицу menu
class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    composition = db.Column(db.JSON, nullable=False)
    weight = db.Column(db.Integer, nullable=True)
    meal_type = db.Column(db.String(20), nullable=True) # используется в меню завтрак/обед

    
    def __init__(self, name, price, composition, weight, meal_type):
        self.name = name
        self.price = price
        self.composition = composition
        self.meal_type = meal_type
        self.weight = weight

    def __repr__(self):
        return f'<Menu {self.id}>'
