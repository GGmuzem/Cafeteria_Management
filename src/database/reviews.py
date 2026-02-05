from config import db
# Здесь мы инициализируем и проверяем таблицу reviews (отзывы)
class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), db.ForeignKey('user.login'), nullable=False)
    review = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=False)

    def __init__(self, user, review, rating, date, menu_id):
        self.user = user
        self.review = review
        self.rating = rating
        self.date = date
        self.menu_id = menu_id

    def __repr__(self):
        return f'<Review {self.id}>'
