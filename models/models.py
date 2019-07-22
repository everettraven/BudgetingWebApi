import json
from flask_sqlalchemy import SQLAlchemy
import datetime
import random

db = SQLAlchemy()

#Create a User class and db model
class User(db.Model):

    #create the columns to be used in the user table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))
    spendingLimit = db.Column(db.Float)
    #Add A Saving Goal When I Get WiFi again
    
    #table relationship to the categories table
    categories = db.relationship('Category', backref='user', lazy=True)

    #initialization function
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    #function to add a category for the user
    def add_category(self, Category):
        self.categories.append(Category)
    
    def change_spending_limit(self, value):
        self.spendingLimit = value
    
    #function to serialize the objectinto a JSON object
    def serialize(self):
        return{
                "id": self.id,
                "username": self.username,
                "spendingLimit": self.spendingLimit,
                "categories": [e.serialize() for e in self.categories]
        }

#Create the Category class and db model
class Category(db.Model):

    #Create the Category variables and db table columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    #Create a relationship to the expenses table for this category
    expenses = db.relationship('Expense', backref='category', lazy=True)

    #link back to the User table with a foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #initialization function
    def __init__(self, name):
        self.name = name
    
    #function to add an expense to the category
    def add_expense(self, Expense):
        self.expenses.append(Expense)
    
    #function to serialize the object to a JSON object
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "expenses": [e.serialize() for e in self.expenses]
            
        }

#Expense class and db model
class Expense(db.Model):

    #Create the Expense variables and db columns
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    amount = db.Column(db.Float)
    location = db.Column(db.String(200))
    date = db.Column(db.DateTime)

    #link back to the categories table
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    #initialization function
    def __init__(self, description, amount, location=None, date=None):
        self.description = description
        self.amount = amount
        if location is not None:
            self.location = location
        else:
            self.location = "unspecified"
        if date is not None:
            self.date = date
        else:
            self.date = datetime.datetime.now()
    
    #serialization function
    def serialize(self):
        return{
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "location": self.location,
            "date": self.date

        }         

        