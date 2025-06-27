from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

app = Flask(__name__)
app.secret_key = "Secret Key"
api_key = "YOUR_API_KEY"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@db:3306/flaskdb'
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

# DB Functions
def get_user_by_id(user_id: int):
    user = Data.query.get(user_id)
    if user:
        return f"User ID: {user.id}, Name: {user.name}, Age: {user.age}, Birth State: {user.birthstate}"
    return "User not found."

def create_user_func(name: str, age: int, birthstate: str):
    new_user = Data(name=name, age=age, birthstate=birthstate)
    db.session.add(new_user)
    db.session.commit()
    return f"User {name} created."

def update_user_func(user_id: int, name=None, age=None, birthstate=None):
    user = Data.query.get(user_id)
    if not user:
        return "User not found."
    user.name = name or user.name
    user.age = age or user.age
    user.birthstate = birthstate or user.birthstate
    db.session.commit()
    return f"User ID {user_id} updated."

def delete_user_func(user_id: int):
    user = Data.query.get(user_id)
    if not user:
        return "User not found."
    db.session.delete(user)
    db.session.commit()
    return f"User ID {user_id} deleted."


# Wrapper functions to parse string input for LangChain tools

def get_user_tool_func(input_str: str):
    try:
        user_id = int(input_str.strip())
    except Exception:
        return "Invalid user ID. Please provide an integer."
    return get_user_by_id(user_id)

def create_user_tool_func(input_str: str):
    # Expected format: "name, age, birthstate"
    parts = [part.strip() for part in input_str.split(",")]
    if len(parts) != 3:
        return "Invalid input format. Expected: name, age, birthstate"
    name, age_str, birthstate = parts
    try:
        age = int(age_str)
    except Exception:
        return "Invalid age. Please provide an integer."
    return create_user_func(name, age, birthstate)

def update_user_tool_func(input_str: str):
    # Expected format: "user_id, name, age, birthstate"
    parts = [part.strip() for part in input_str.split(",")]
    if len(parts) != 4:
        return "Invalid input format. Expected: user_id, name, age, birthstate"
    user_id_str, name, age_str, birthstate = parts
    try:
        user_id = int(user_id_str)
        age = int(age_str)
    except Exception:
        return "Invalid user ID or age. Please provide integers."
    return update_user_func(user_id, name, age, birthstate)

def delete_user_tool_func(input_str: str):
    try:
        user_id = int(input_str.strip())
    except Exception:
        return "Invalid user ID. Please provide an integer."
    return delete_user_func(user_id)


# tools using these wrapper functions

tools = [
    Tool.from_function(
        name="get_user_tool",
        description="Get user info by ID. Input: user ID as an integer.",
        func=get_user_tool_func
    ),
    Tool.from_function(
        name="create_user_tool",
        description="Create a new user with name, age, and birthstate. Input format: name, age, birthstate",
        func=create_user_tool_func
    ),
    Tool.from_function(
        name="update_user_tool",
        description="Update a user by ID and new fields. Input format: user_id, name, age, birthstate",
        func=update_user_tool_func
    ),
    Tool.from_function(
        name="delete_user_tool",
        description="Delete a user by ID. Input: user ID as an integer.",
        func=delete_user_tool_func
    ),
]

# Format tool names for prompt template
tool_names = ", ".join([tool.name for tool in tools])

# Custom agent prompt template
template = f"""
You are a smart assistant that manages a user database using the following tools:
- get_user_tool: Get user info by ID
- create_user_tool: Create a new user with name, age, and birthstate
- update_user_tool: Update a user by ID and new fields
- delete_user_tool: Delete a user by ID

When answering, follow this format:
Thought: Do I need to use a tool? Yes
Action: the action to take, one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action

If no tool is needed:
Thought: Do I need to use a tool? No
Final Answer: [answer to the user]
"""

prompt = PromptTemplate.from_template(template)

agent = initialize_agent(
    tools=tools,
    llm=OpenAI(openai_api_key=api_key, temperature=0),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"prefix": prompt.template},
    verbose=True,
)

def run_agent(user_input: str):
    with app.app_context():
        return agent.run(user_input)

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

# Agentic AI
@app.route('/ask-ai', methods=['POST'])
def ask_ai():
    data = request.get_json()
    user_input = data.get("input", "")
    if not user_input:
        return jsonify({"error": "Missing input"}), 400

    try:
        result = run_agent(user_input)
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
