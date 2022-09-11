from flask import Flask, render_template, url_for, request, redirect, send_from_directory, send_file, flash, jsonify, Blueprint, Response, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager, UserMixin
from flask_mail import Mail, Message
from flask_cors import CORS
from flask_restful import Resource, Api
from datetime import datetime
from werkzeug.utils import secure_filename
import random
import os

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

DB_NAME = "database.db"

UPLOAD_FOLDER = './images/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

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
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mail = Mail(app)
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    password = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    security_key = db.Column(db.String(65))
    validated = db.Column(db.Boolean(), default=False)
    notifications = db.relationship('Notifications', backref="user")
    address = db.Column(db.Text)
    baskets = db.relationship('Basket', backref="user")
    categories = db.relationship('Category', backref="user")

class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(150))
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

db.create_all()

def validate_user_with_email(address, securitykey, name):
    msg = Message("""verify your email""", sender = 'drive1.banerjee.armaan@outlook.com', recipients=[address])
    msg.html = f"""
    <html>
        <body>
            <h1> Hi {name}</h1>
            <p>Thank you for creating an acount on my website.</p>
            <p>Please validate your email <a href='http://localhost:5040/user/validate/{securitykey}'>here</a>
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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
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
        return redirect('home')
    else:
        return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        name = request.form["name"]
        password = request.form["password"]
        usern = db.session.query(User).filter(User.name == name).first_or_404()
        eid = usern.id
        if not usern:
            return redirect(url_for("signup"))
        elif check_password_hash(usern.password, password):
            login_user(usern, remember=True)
            return redirect(f"/dashboard")
        else:
            return render_template("login.html", msg="password is incorrect")
    else:
        return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")

@login_required
@app.route("/user/validate/<securitykey>")
def validate_user(securitykey):
    user = db.session.query(User).filter(User.security_key == securitykey).first()
    if user.id == current_user.id:
        user.validated = True
        db.session.commit()
        return redirect("/home")
    else:
        return redirect("/home")

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
    for item in range(data["items"]):
        new_item = Item(category_id = id)
        db.session.add(new_item)
        new.stock += 1
    db.session.commit()

@login_required
@app.route("/view/add", methods=["POST"])
def view_add_category():
    if request.method == 'POST':
        name = request.form["name"]
        new = Category(name = name, user_id = current_user.id, stock=0)
        db.session.add(new)
        db.session.commit()
        id = getattr(new, "id")
        for i in range(int(request.form["stock"])):
            new_item = Item(category_id = id)
            db.session.add(new_item)
            new.stock += 1
        
        db.session.commit()
        idx = getattr(new, "id")
        return jsonify({"id": idx})

@login_required
@app.route("/views/add")
def please_view_add_with_params():
    pass

@app.route("/api/add/basket")
def api_add_basket():
    id = request.args.to_dict(flat=False)["id"]
    user_id = request.args.get("user_id")
    new = Basket(user_id=user_id)
    db.session.add(new)
    bid = getattr(new, "id")
    for i in id:
        item = Item.query.filter_by(id=i).first()
        categorid = item.category_id
        category = Category.query.filter_by(id=categorid).first()
        category.stock -= 1
        item.basket_id = bid
    db.session.commit()

@app.route("/api/checkout")
def checkout():
    id = request.args.get("id")
    basket = Basket.query.filter_by(id=id).first()
    userid = basket.user_id
    user = User.query.filter_by(user_id=userid).first()
    name = user.name
    items = basket.items
    for item in items:
        catid = item.category_id
        category = Category.query.filter_by(id=catid).first()
        seller = category.user_id
        new = Notifications(user_id = seller, text=f"{name} wants a {category.name}")
        db.session.add(new)

    db.session.commit()

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route("/api/uploads", methods=['POST'])
def api_uploads():
    categoryid = request.args.get("id")
    category = Category.query.filter_by(id=categoryid).first()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        names = []
        for file in request.files.getlist('file'):
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                names.append(filename)
                name = os.path.join(f"{app.config['UPLOAD_FOLDER']}{category.name}/", filename)
                file.save(name)
    
    return jsonify(msg="uploaded")
    
@app.route("/upload", methods=["POST", "GET"])
def upload_stuff():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        names = []
        for file in request.files.getlist('file'):
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                names.append(filename)
                name = os.path.join(f"{app.config['UPLOAD_FOLDER']}", filename)
                file.save(name)
        
        return "uploaded"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file multiple>
      <input type=submit value=Upload>
    </form>
    ''' 

@app.route("/add")
def add_stuff():
    return render_template("add.html")

@login_required
@app.route("/home")
def home():
    return f"<h1>Hi {current_user.name} |  {current_user.id}</h1>"
    
if __name__ == "__main__":
    app.run(port=5040, host="0.0.0.0", debug=True)