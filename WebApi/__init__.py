from flask import Flask, jsonify, request, Response
from flask_jwt_extended import(JWTManager, jwt_required, jwt_refresh_token_required, 
    create_access_token, create_refresh_token, get_jwt_identity)
import os
from models.models import *

#Create a variable with the location of the sqlite db
db_url = "sqlite:////tmp/temp.db"

#initialize the application
app = Flask(__name__)

#add the app config values
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['JWT_SECRET_KEY'] = "MySuperSecretBudgetingAPIJWTKey" #change this in the future

#Add the JWT Manager
JWTManager(app)

#setup the db
db.app = app
db.init_app(app)
db.create_all()

codes = []


#Create the register app route
@app.route("/register", methods=['POST'])
def register():
    if not request.json:
        return jsonify(error="Bad Request"), 400
    
    data = request.json

    if "User" in data:
        d = data["User"]
        new_user = User(d["username"], d["password"])
        db.session.add(new_user)
        db.session.commit()
    
    else:
        return jsonify(error="Bad Request"), 400
    
    return jsonify(new_user.serialize()), 200


#Create the login route
@app.route("/auth", methods=['POST'])
def login():
    if not request.json:
        return jsonify(error="Bad Request"), 400
    
    data = request.json

    if "User" in data:
        d = data["User"]
        login_as = User.query.filter(User.username == d["username"], User.password == d["password"]).first()
        if login_as is not None:
            #Create the JWT for the response
            access_token = create_access_token(identity=login_as.id)
            refresh_token = create_refresh_token(identity=login_as.id)

        else:
            return jsonify(error="The user doesn't exist, please register as a user before continuing"), 400
    else:
        return jsonify(error="Bad Request"), 400
    
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200



#Create the refresh route to refresh the access token
@app.route("/auth/refresh", methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    
    return jsonify(access_token=access_token), 200


#Create the /categories routes
@app.route("/categories", methods=['GET'])
@jwt_required
def get_categories():
    


#Create the /categories/add route
@app.route("/categories/add", methods=['POST'])
@jwt_required
def add_category():
    if not request.json:
        return jsonify(error="Bad Request"), 400
    
    data = request.json

    current_user = get_jwt_identity()

    if "Category" in data:
        d = data["Category"]
        new_cat = Category(d["name"])
        user_to_update = User.query.filter(User.id == current_user).first()
        user_to_update.add_category(new_cat)
        db.session.commit()
    else:
        return jsonify(error="Bad Request"), 400

    updated_user = User.query.filter(User.id == current_user).first()

    return jsonify([updated_user.serialize()]), 200
    

#Create the AddExpense route
@app.route("/expenses/add", methods=['POST'])
@jwt_required
def add_expense():
    if not request.json:
        return jsonify(error="Bad Request"), 400
    
    data = request.json

    current_user = get_jwt_identity()

    if "Expense" in data:
        d = data["Expense"]
        descrip = d["description"]
        amount = d["amount"]
        if "location" in d:
            loc = d["location"]
        else:
            loc = None
        
        if "date" in d:
            date = d["date"]
        else:
            date = None

        new_exp = Expense(descrip, amount, location=loc, date=date)

        user_to_update = User.query.filter(User.id == current_user).first()

        for i in user_to_update.categories:
            if i.id == d["catID"]:
                i.add_expense(new_exp)

        db.session.commit()

    else:
        return jsonify(error="Bad Request"), 400
    
    get_user = User.query.filter(User.id == current_user).first()

    return jsonify([get_user.serialize()]), 200


#Create a get user route
@app.route("/user", methods=['GET', 'POST'])
@jwt_required
def user_info():
    
    current_user = get_jwt_identity()

    if request.method == 'GET':

        get_user = User.query.filter(User.id == current_user).first()

        return jsonify([get_user.serialize()]), 200

    else:
        
        if not request.json:
            return jsonify(error="Bad Request"), 400
        
        data = request.json

        if "User" in data:
            d = data["User"]

            user = User.query.filter(User.id == current_user).first()

            user.spendingLimit = d["spendingLimit"]
            db.session.commit()

            get_user = User.query.filter(User.id == current_user).first()

            return jsonify([get_user.serialize()]), 200
        else:

            return jsonify(error="Bad Request"), 400
            


