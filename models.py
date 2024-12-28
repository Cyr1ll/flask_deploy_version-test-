from datetime import  date

from sqlalchemy import nullsfirst

from extensions import db

class TestDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    purchase_amount = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<TestDB {self.customer_name}, {self.purchase_amount}, {self.purchase_date}>"
