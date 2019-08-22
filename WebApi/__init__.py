from flask import Flask, jsonify, request, Response
from flask_jwt_extended import(JWTManager, jwt_required, jwt_refresh_token_required, 
    create_access_token, create_refresh_token, get_jwt_identity)
import os
from models.models import *
from extensions import OAuth

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


#Create the register app route to register a new user
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

#Create an endpoint to register a developer
@app.route("/developer/register", methods=['POST'])
def dev_reg():
    if not request.json:
        return jsonify(error="Bad Request"), 400
    
    data = request.json

    if "name" in data:
        name = data["name"]
    else:
        return jsonify(error="Bad Request"), 400
    
    if "redirect_uri" in data:
        redirect = data["redirect_uri"]
    else:
        return jsonify(error="Bad Request"), 400

    dev = Developer(name, redirect)
    dev.generate_id()
    dev.generate_secret()
    db.session.add(dev)
    db.session.commit()

    dev_check = Developer.query.filter(Developer.client_id == dev.client_id, Developer.client_secret == dev.client_secret).first()

    return jsonify(dev_check.serialize()), 200
        


#Create the login route -> Will return an auth code?
@app.route("/login", methods=['POST'])
def login():

    if not request.json:
        return jsonify(error="Bad Request"), 400

    # if not request.args.get('response_type'):
    #     return jsonify(error="Bad Request"), 400

    # if not request.args.get('client_id'):
    #     return jsonify(error="Bad Request"), 400
    
    data = request.json

    if "User" in data:
        d = data["User"]
        login_as = User.query.filter(User.username == d["username"], User.password == d["password"]).first()
        if login_as is not None:
            #Create the auth code
            code = AuthCode()
            login_as.add_code(code)
            db.session.commit()

        else:
            return jsonify(error="The user doesn't exist, please register as a user before continuing"), 400
    else:
        return jsonify(error="Bad Request"), 400
    
    return jsonify(authorization_code = code.code), 200

#create a route to exchange the code
@app.route("/auth", methods=['POST'])
@OAuth
def auth(access, refresh, code):
    if code is not None:
        code_check = AuthCode.query.filter(AuthCode.code == code, AuthCode.code_used == False).first()

        if code_check is not None:
            user = User.query.filter(User.id == code_check.user_id).first()

        else:
            return jsonify(error="That code doesn't exist"), 400

        if user is not None:
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            code_check.code_used = True

            db.session.commit()

            return jsonify(access_token=access_token, refresh_token=refresh_token), 200

        else:
            return jsonify(error="Failed to find the authorization code."), 400
    
    elif access:
        return jsonify(msg="sending an access token to this endpoint does absolutely nothing."), 200

    elif refresh:
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        return jsonify(access_token=access_token), 200
    

#Create the /categories routes
@app.route("/categories", methods=['GET'])
@jwt_required
def get_categories():
    current_user = get_jwt_identity()
    
    user = User.query.filter(User.id == current_user).first()

    categories = user.categories

    return jsonify([e.serialize() for e in categories]), 200

@app.route("/categories/<cat_id>", methods=['GET'])
@jwt_required
def get_category_id(cat_id):
    current_user = get_jwt_identity()

    user = User.query.filter(User.id == current_user).first()

    categories = user.categories

    for i in categories:
        if i.id == int(cat_id):
            return jsonify(i.serialize()), 200

    return jsonify(error="That category doesn't exist for this user"), 400

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
    
#Create the /categories/update route
@app.route("/categories/<cat_id>/update", methods=['POST'])
@jwt_required
def category_update(cat_id):
    if not request.json:
        return jsonify(error="Bad Request"), 400

    current_user = get_jwt_identity()

    user = User.query.filter(User.id == current_user).first()

    categories = user.categories

    for i in categories:
        if i.id == int(cat_id):
            category = i

    data = request.json

    if "Category" in data:
        d = data["Category"]

        if "name" in d:
            category.name = d["name"]
        
        #add more here when i get wifi. like a budgetary restriction...
        db.session.commit()
    else:
        return jsonify(error="Bad Request"), 400
    
    return jsonify(category.serialize()), 200



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


#Create a user route. Will allow get to get user info and will allow updating user info
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

            # Only update a user's spending limit if they already exist
            user.spendingLimit = d["spendingLimit"]
            db.session.commit()

            get_user = User.query.filter(User.id == current_user).first()

            return jsonify([get_user.serialize()]), 200
        else:

            return jsonify(error="Bad Request"), 400
            


