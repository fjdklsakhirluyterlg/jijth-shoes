import math
from unicodedata import name
from flask import Flask, render_template, url_for, request, redirect, send_from_directory, send_file, flash, jsonify, Blueprint, Response, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager, UserMixin
from flask_mail import Mail, Message
from flask_cors import CORS
from flask_restful import Resource, Api
from datetime import datetime
import random

app = Flask(__name__)
api = Api(app)
mail = Mail(app)
CORS(app, resources={r"*": {"origins": "*"}})

login_manager = LoginManager()
login_manager.login_view = "/login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.errorhandler(500)
def internal_server_error(e):
    return f"Something went wrong : {e}", 500

@app.errorhandler(405)
def method_not_allowed(e):

    if request.path.startswith('/api/'):
        
        return jsonify(message="Method Not Allowed"), 405
    else:
        return "wrong method!"

@app.errorhandler(404)
def page_not_found(e):
    return f"Sorry could not find this"

app.register_error_handler(404, page_not_found)

DB_NAME = "dataaabbb.db"

app.config['SQLALCHEMY_DATABASE_URI'] =f'sqlite:///{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "key"
app.config['MAIL_SERVER']='smtp.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'drive1.banerjee.armaan@outlook.com'
app.config['MAIL_PASSWORD'] = 'Transport11.'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
mail = Mail(app)
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    security_key = db.Column(db.String(65))
    validated = db.Column(db.Boolean(), default=False)
    notifications = db.relationship('Notifications', backref="user")
    address = db.Column(db.Text)
    

class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(150))
    read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    basket_id = db.Column(db.Integer, db.ForeignKey('basket.id'), nullable=True, default=None)

class Basket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    items = db.relationship('Item', backref="basket")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    items = db.Column(db.Integer, db.ForeignKey('item.id'))
    stock = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

def validate_user_with_email(address, securitykey, name):
    msg = Message("""verify your email""", sender = 'drive1.banerjee.armaan@outlook.com', recipients=[address])
    msg.html = f"""
    <html>
        <body>
            <h1> Hi {name}</h1>
            <p>Thank you for creating an acount on my website.</p>
            <p>Please validate your email <a href='http://localhost:5050/user/validate/{securitykey}'>here</a>
            <p>Please validate your email <a href='https://murmuring-tundra-00105.herokuapp.com/user/validate/{securitykey}'>here</a>
        </body>
    </html>
    """
    mail.send(msg)
    return {"msg": "sent"}

def mank_random_long_id(length):
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    result = ""
    charactersLength = len(characters) - 1
    for i in range(length):
        result += characters[random.randint(0, charactersLength)]
    return result

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        # telephone = request.form["telephone"]
        password = request.form["password"]
        password2 = request.form["password2"]
        if password != password2:
            return render_template("signup.html", msg="pasword does not match")
        
        security_key = mank_random_long_id(64)
        news = User(name=name, email=email, password=generate_password_hash(password, method='sha256'), security_key=security_key)
        db.session.add(news)
        db.session.commit()
        login_user(news, remember=True)
        try:
            validate_user_with_email(address=email, securitykey=security_key, name=name)
        except:
            pass
        return redirect('/dashboard')
    else:
        return render_template("signup.html")

@app.route("/api/add/item", methods=["POST"])
def api_add_item():
    data = request.get_json()
    category = data["category"]
    catego = Category.query.filter_by(name=category).first()
    catego.stock += 1
    item = Item(category_id=catego.id)
    db.session.add(item)
    db.session.commit()

@app.route("/api/add/category")
def api_add_category():
    data = request.get_json()
    name = data["name"]
    user_id = data["user_id"]
    new = Category(name=name, user_id=user_id, stock=0)
    db.session.add(new)
    id = getattr(new, "id")
    for item in data["items"]:
        new_item = Item(category_id = id)
        db.session.add(new_item)
        new.stock += 1
    db.session.commit()