from config import db
from datetime import datetime
# Здесь мы инициализируем и проверяем таблицу requests

class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product = db.Column(db.String(255), db.ForeignKey('storage.name'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(25), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    price_per_unit = db.Column(db.Integer, nullable=True)

    def __init__(self, user, product, amount, status, date, price_per_unit=0):
        self.user = user
        self.product = product
        self.amount = amount
        self.status = status
        self.date = date
        self.price_per_unit = price_per_unit

    def __repr__(self):
        return f'<Request {self.id}>'
