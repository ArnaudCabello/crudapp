from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
app = Flask(__name__)
app.secret_key = "Secret Key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{db_user}:{db_password}@db:3306/flaskdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    birthstate = db.Column(db.String(100), nullable=False)

    def __init__(self, name, age, birthstate):
        self.name = name
        self.age = age
        self.birthstate = birthstate

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    users = Data.query.all()
    return render_template("index.html", users=users)

@app.route('/insert', methods=['POST'])
def insert():
    name = request.form['name']
    age = request.form['age']
    birthstate = request.form['birthstate']

    new_user = Data(name, age, birthstate)
    db.session.add(new_user)
    db.session.commit()

    flash("User inserted successfully")
    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update():
    user_id = request.form.get('id')
    user = Data.query.get(user_id)

    if not user:
        flash("User not found")
        return redirect(url_for('index'))

    user.name = request.form['name']
    user.age = request.form['age']
    user.birthstate = request.form['birthstate']
    db.session.commit()

    flash("User updated successfully")
    return redirect(url_for('index'))

@app.route('/delete/<int:id>/', methods=['GET', 'POST'])
def delete(id):
    user = Data.query.get(id)
    if not user:
        flash("User not found")
        return redirect(url_for('index'))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully")
    return redirect(url_for('index'))

# REST API: Get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    users = Data.query.all()
    return jsonify([{"id": u.id, "name": u.name, "age": u.age, "birthstate": u.birthstate} for u in users])

# REST API: Get user by ID
@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    user = Data.query.get_or_404(id)
    return jsonify({"id": user.id, "name": user.name, "age": user.age, "birthstate": user.birthstate})

# REST API: Create new user
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    birthstate = data.get('birthstate')

    if not name or age is None or not birthstate:
        return jsonify({"error": "Missing fields"}), 400

    new_user = Data(name, age, birthstate)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created", "id": new_user.id}), 201

# REST API: Update user
@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = Data.query.get_or_404(id)
    data = request.get_json()

    user.name = data.get('name', user.name)
    user.age = data.get('age', user.age)
    user.birthstate = data.get('birthstate', user.birthstate)

    db.session.commit()
    return jsonify({"message": "User updated"})

# REST API: Delete user
@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = Data.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)