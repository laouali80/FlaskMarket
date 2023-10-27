from market import db, login_manager
# setter
from market import bcrypt
from flask_login import UserMixin

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# use to check if the user is login or not at each refresh 
# always change the return from User.get() to User.query.get(int(user_id)) check also the table (User)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email = db.Column(db.String(length=50), nullable=True, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=True)
    budget = db.Column(db.Integer(), nullable=True, default=1000)

    # item refer the Item model, backref is use to know the owner of an item, lazy grabs all the items of the user in sql
    items = db.relationship('Item', backref='owned_user', lazy=True)

    # config the way that we want to receive back an attribute and the way that we want to set an attribute
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')


    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'${str(self.budget)[:-3]},{str(self.budget)[-3:]}.00'
        else:
            return f'${str(self.budget)}.00'

    def can_purchase(self, item):
        # checking if the user has enough budget
        return self.budget >= item.price
    
    def can_sell(self, item):
        # checking if the user has the item
        return item in self.items


class Item(db.Model):    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False)
    possesion = db.Column(db.Integer(), db.ForeignKey('user.id')) 
    date = db.Column(db.DateTime(), default=datetime.now())
    owner = db.Column(db.Integer())

    def __repr__(self):
        return f'Item{self.name}'

    def buy(self, user):

        # assign to the current user the item
        self.owner = user.id
        self.possesion = user.id
        # debitting the user account
        user.budget -= self.price

        db.session.commit()

    def sell(self, user):
        # depossess the current user the item
        self.possesion = None

        # crediting the user account
        user.budget += self.price

        db.session.commit()

