from src.database import db
from src.database.users import User

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(255), db.ForeignKey('user.login'), nullable=False)
    type_of_transaction = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __init__(self, user, type_of_transaction, amount, date):
        self.user = user
        self.type_of_transaction = type_of_transaction
        self.amount = amount
        self.date = date

    def __repr__(self):
        return f'<History {self.id}>'