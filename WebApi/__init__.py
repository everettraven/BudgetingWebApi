from flask import Flask, jsonify, request, Response
from flask_jwt_extended import(JWTManager, jwt_required, jwt_refresh_token_required, 
    create_access_token, create_refresh_token, get_jwt_identity)
import os
from models.models import *
from WebApi.extensions import OAuth

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

# create a test developer account for testing purposes
test_dev = Developer("TestDev", "www.testdev.com")
test_dev.client_id = "testclientid"
test_dev.client_secret = "testclientsecret"
db.session.add(test_dev)
db.session.commit()

# Create the register app route to register a new user.
@app.route("/user/register", methods=['POST'])
def register():
    # Try getting the client_id and client_secret from the header. If you can't then throw an msg.
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']
    except:
        return jsonify(msg="You are either missing the client_id header, the client_secret header, or both"), 400

    # Get the developer correlated to that client_id and client_secret
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret).first()
    
    # If the developer exists then allow them to continue with the request
    if developer is not None:
        # Make sure that JSON data is sent with the request
        if not request.json:
            return jsonify(msg="Bad Request"), 400
        
        data = request.json

        # Check to ensure that the JSON data contains the required data fields.
        if ("username" in data) and ("password" in data):
            new_user = User(data["username"], data["password"])
            # Check if the optional field spendingLimit is in the JSON data.
            if "spendingLimit" in data:
                new_user.change_spending_limit(data["spendingLimit"])
            
            db.session.add(new_user)
            db.session.commit()
        else:
            return jsonify(msg="You must include both the username and password data fields in your JSON body"), 400
        
        return jsonify(new_user.serialize()), 200
    else:
        return jsonify(msg="You are not authorized to use this API. Please register as a developer to begin using this api."), 400

# Create an endpoint to register a developer
@app.route("/developer/register", methods=['POST'])
def dev_reg():
    # Check to ensure that the request sent is in JSON format
    if not request.json:
        return jsonify(msg="Bad Request"), 400
    
    data = request.json

    # Check for the required fields to create a new developer in the system
    if ("name" in data) and ("redirect_uri" in data):
        name = data["name"]
        redirect = data["redirect_uri"]
    else:
        return jsonify(msg="You must include the name and redirect_uri data fields in your JSON body to create a new developer"), 400
    

    # Create the new developer
    dev = Developer(name, redirect)
    dev.generate_id()
    dev.generate_secret()
    db.session.add(dev)
    db.session.commit()

    # Get the newly created developer from the database to ensure that it is created
    dev_check = Developer.query.filter(Developer.client_id == dev.client_id, Developer.client_secret == dev.client_secret).first()

    # Return the developer information so it can be shown to them.
    return jsonify(dev_check.serialize()), 200
        


# Create the login route. Returns an auth code that can be redeemed for a 
@app.route("/user/login", methods=['POST'])
def login():

    # Check the request headers for the client_id and client_secret
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']
    except:
        return jsonify(msg="You must include the client_id and client_secret in your request headers")
    
    # Check to make sure the developer with the given information exists
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret).first()
    
    if developer is not None:
        # Check for json data in the request
        if not request.json:
            return jsonify(msg="You must use JSON to send the data."), 400
        
        data = request.json

        # Check to make sure the required JSON data fields exist in the JSON request body.
        if ("username" in data) and ("password" in data):
            login_as = User.query.filter(User.username == data["username"], User.password == data["password"]).first()
            if login_as is not None:
                # Create the auth code
                code = AuthCode()
                login_as.add_code(code)
                db.session.commit()

            else:
                return jsonify(msg="This user doesn't exist, please register as a user before continuing"), 400
        else:
            return jsonify(msg="The username and password data fields are required in the JSON body."), 400
    else:
        return jsonify(msg="You are not authorized to use this API. In order to be able to use this API please register as a new developer"), 400
        
    return jsonify(authorization_code = code.code), 200

# Create a route to exchange the code for an access token and refresh token or get a new access token
@app.route("/user/auth", methods=['POST'])
@OAuth
def auth(access, refresh, code):
    # Make sure that it is an authorized developer accessing the api
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']
    except:
        return jsonify(msg="You must include the client_id and client_secret in your request headers"), 400

    # Check if the developer exists
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret)

    # if the developer doesn't exist return the msg from the function
    if developer is None:
        return jsonify(msg="You are not authorized to use this API. In order to be able to use this API please register as a new developer"), 400

    # Check if what is being passed is an authorization code, an access token, or a refresh token
    if code is not None:
        # Attempt to get the code passed in from the database and make sure it doesn't have the used flag.
        code_check = AuthCode.query.filter(AuthCode.code == code, AuthCode.code_used == False).first()

        # If the code exists, try to get the user it belongs to
        if code_check is not None:
            user = User.query.filter(User.id == code_check.user_id).first()
        else:
            return jsonify(msg="That code doesn't exist"), 400

        # Check if the user that the authorization points to exists
        if user is not None:
            # Create an access token and refresh token
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            # Set the code to have the used flag so it can't be used again.
            code_check.code_used = True

            db.session.commit()

            return jsonify(access_token=access_token, refresh_token=refresh_token), 200

        else:
            return jsonify(msg="Failed to find a user with that authorization code."), 400
    
    elif access:
        return jsonify(msg="Sending an access token to this endpoint does absolutely nothing."), 200

    elif refresh:
        # Create a new access token based off of the identity of the refresh token passed in.
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        return jsonify(access_token=access_token), 200
    

# Create the /categories routes
@app.route("/user/categories", methods=['GET'])
@jwt_required
def get_categories():
    # attempt to get the client_id and client_secret headers
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']

    except:
        return jsonify(msg="You must include the client_id and client_secret in your request headers"), 400

    # Check if the developer exists
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret)

    # if the developer doesn't exist return the msg from the function
    if developer is None:
        return jsonify(msg="You are not authorized to use this API. In order to be able to use this API please register as a new developer"), 400

    current_user = get_jwt_identity()
    
    user = User.query.filter(User.id == current_user).first()

    categories = user.categories

    return jsonify([e.serialize() for e in categories]), 200

@app.route("/user/categories/<cat_id>", methods=['GET'])
@jwt_required
def get_category_id(cat_id):
    # attempt to get the client_id and client_secret headers
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']

    except:
        return jsonify(msg="You must include the client_id and client_secret in your request headers"), 400

    # Check if the developer exists
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret)

    # if the developer doesn't exist return the msg from the function
    if developer is None:
        return jsonify(msg="You are not authorized to use this API. In order to be able to use this API please register as a new developer"), 400

    current_user = get_jwt_identity()

    user = User.query.filter(User.id == current_user).first()

    categories = user.categories

    for i in categories:
        if i.id == int(cat_id):
            return jsonify(i.serialize()), 200

    return jsonify(msg="That category doesn't exist for this user"), 400

#Create the /categories/add route
@app.route("/user/categories/add", methods=['POST'])
@jwt_required
def add_category():
    # attempt to get the client_id and client_secret headers
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']

    except:
        return jsonify(msg="You must include the client_id and client_secret in your request headers"), 400

    # Check if the developer exists
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret)

    # if the developer doesn't exist return the msg from the function
    if developer is None:
        return jsonify(msg="You are not authorized to use this API. In order to be able to use this API please register as a new developer"), 400

    if not request.json:
        return jsonify(msg="You must use JSON to send the data."), 400

    data = request.json

    current_user = get_jwt_identity()

    if "name" in data:
        new_cat = Category(data["name"])
        user_to_update = User.query.filter(User.id == current_user).first()
        user_to_update.add_category(new_cat)
        db.session.commit()
    else:
        return jsonify(msg="You must include the name data field in the JSON body."), 400

    updated_user = User.query.filter(User.id == current_user).first()

    return jsonify([updated_user.serialize()]), 200
    
#Create the /categories/update route
@app.route("/user/categories/<cat_id>/update", methods=['POST'])
@jwt_required
def category_update(cat_id):
    # attempt to get the client_id and client_secret headers
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']

    except:
        return jsonify(msg="You must include the client_id and client_secret in your request headers"), 400

    # Check if the developer exists
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret)

    # if the developer doesn't exist return the msg from the function
    if developer is None:
        return jsonify(msg="You are not authorized to use this API. In order to be able to use this API please register as a new developer"), 400

    if not request.json:
        return jsonify(msg="You must use JSON to send the data."), 400

    current_user = get_jwt_identity()

    user = User.query.filter(User.id == current_user).first()

    categories = user.categories

    for i in categories:
        if i.id == int(cat_id):
            category = i

    data = request.json

    if "name" in data:
        category.name = data["name"]
        db.session.commit()
    else:
        return jsonify(msg="You must include the name data field in the JSON body"), 400
    
    return jsonify(category.serialize()), 200


#Get all expenses from a category
@app.route("/user/categories/<cat_id>/expenses", methods=['GET'])
@jwt_required
def get_expenses(cat_id):
    # attempt to get the client_id and client_secret headers
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']

    except:
        return jsonify(msg="You must include the client_id and client_secret in your request headers"), 400

    # Check if the developer exists
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret)

    # if the developer doesn't exist return the msg from the function
    if developer is None:
        return jsonify(msg="You are not authorized to use this API. In order to be able to use this API please register as a new developer"), 400

    current_user = get_jwt_identity()

    user = User.query.filter(User.id == current_user).first()

    categories = user.categories

    for i in categories:
        if i.id == int(cat_id):
            return jsonify([e.serialize() for e in i.expenses]), 200
    

# Add an expense to a category
@app.route("/user/categories/<cat_id>/expenses/add", methods=['POST'])
@jwt_required
def add_expense(cat_id):
    # attempt to get the client_id and client_secret headers
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']

    except:
        return jsonify(msg="You must include the client_id and client_secret in your request headers"), 400

    # Check if the developer exists
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret)

    # if the developer doesn't exist return the msg from the function
    if developer is None:
        return jsonify(msg="You are not authorized to use this API. In order to be able to use this API please register as a new developer"), 400

    if not request.json:
        return jsonify(msg="You must send the data as JSON data"), 400
    
    data = request.json

    current_user = get_jwt_identity()

    if ("description" in data) and ("amount" in data):
        descrip = data["description"]
        amount = data["amount"]
        if "location" in data:
            loc = data["location"]
        else:
            loc = None
        
        if "date" in data:
            date = data["date"]
        else:
            date = None

        # Create a new expense and add it to the current user
        new_exp = Expense(descrip, amount, location=loc, date=date)

        user_to_update = User.query.filter(User.id == current_user).first()

        for i in user_to_update.categories:
            if i.id == int(cat_id):
                i.add_expense(new_exp)

        user_to_update.add_to_spent(new_exp.amount)

        db.session.commit()
    
    else:
        return jsonify(msg="You must include the description and the amount data fields in the the JSON body"), 400
    
    # Return the new user data
    get_user = User.query.filter(User.id == current_user).first()

    return jsonify([get_user.serialize()]), 200
    
@app.route("/user/categories/expenses/<expense_id>/update", methods=['POST'])
@jwt_required
def edit_expense(expense_id):
    # attempt to get the client_id and client_secret headers
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']

    except:
        return jsonify(msg="You must include the client_id and client_secret in your request headers"), 400

    # Check if the developer exists
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret)

    # if the developer doesn't exist return the msg from the function
    if developer is None:
        return jsonify(msg="You are not authorized to use this API. In order to be able to use this API please register as a new developer"), 400

    if not request.json:
        return jsonify(msg="You must send the data as JSON"), 400
    
    data = request.json

    current_user = get_jwt_identity()

    # Get the expense to update
    expense_update = Expense.query.filter(Expense.id == expense_id).first()

    if "description" in data:
        expense_update.description = data["description"]

    if "amount" in data:
        expense_update.amount = data["amount"]

    if "location" in data:
        expense_update.location = data["location"]
        
    if "date" in data:
        expense_update.date = data["date"]

    db.session.commit()
    
    # return the new user data
    get_user = User.query.filter(User.id == current_user).first()

    return jsonify([get_user.serialize()]), 200


#Create a user route. Will allow get to get user info and will allow updating user info
@app.route("/user", methods=['GET', 'POST'])
@jwt_required
def user_info():
    # attempt to get the client_id and client_secret headers
    try:
        client_id = request.headers['client_id']
        client_secret = request.headers['client_secret']

    except:
        return jsonify(msg="You must include the client_id and client_secret in your request headers"), 400

    # Check if the developer exists
    developer = Developer.query.filter(Developer.client_id == client_id, Developer.client_secret == client_secret)

    # if the developer doesn't exist return the msg from the function
    if developer is None:
        return jsonify(msg="You are not authorized to use this API. In order to be able to use this API please register as a new developer"), 400

    
    current_user = get_jwt_identity()

    if request.method == 'GET':

        get_user = User.query.filter(User.id == current_user).first()

        return jsonify([get_user.serialize()]), 200

    else:
        
        if not request.json:
            return jsonify(msg="The data must be sent as JSON"), 400
        
        data = request.json

        # Get the user and update their spending limit
        user = User.query.filter(User.id == current_user).first()

        if "spendingLimit" in data:
            user.spendingLimit = data["spendingLimit"]
            db.session.commit()
        else:
            return jsonify(msg="You must include the spendingLimit data field in your JSON data to update the user's information"), 400

        get_user = User.query.filter(User.id == current_user).first()

        return jsonify([get_user.serialize()]), 200

            


