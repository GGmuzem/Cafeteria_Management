from config import db
from datetime import datetime
# Здесь мы инициализируем и проверяем таблицу history
class history_operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type_of_transaction = db.Column(db.String(25), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user, type_of_transaction, amount):
        self.user = user
        self.type_of_transaction = type_of_transaction
        self.amount = amount

    def __repr__(self):
        return f'<History {self.id}>'
