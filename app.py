"""
app.py
-------
A RESTful Task Manager API built with Flask.

Features:
- User signup and login with JWT-based authentication
- CRUD operations on tasks (Create, Read, Update, Delete)
- Each user can only see and manage their own tasks
- SQLite database (file-based, zero setup — swap for MySQL/Postgres in production)
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)

db = SQLAlchemy(app)
jwt = JWTManager(app)


# ---------------------------------------------------------------
# Database Models
# ---------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
        }


# ---------------------------------------------------------------
# Home Route (so visiting the base URL shows something useful
# instead of a "Not Found" error)
# ---------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Task Manager REST API is running.",
        "note": "This is a backend API with no visual interface. Use Postman or curl to interact with the endpoints below.",
        "endpoints": {
            "POST /signup": "Create a new user account (body: username, password)",
            "POST /login": "Log in and receive a JWT access token (body: username, password)",
            "GET /tasks": "Get all tasks for the logged-in user (requires Bearer token)",
            "POST /tasks": "Create a new task (requires Bearer token, body: title, description)",
            "PUT /tasks/<id>": "Update a task (requires Bearer token)",
            "DELETE /tasks/<id>": "Delete a task (requires Bearer token)",
        },
        "github": "https://github.com/saraq0112/task-manager-api",
    }), 200


# ---------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already exists"}), 409

    user = User(
        username=username, password_hash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "user created successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200


# ---------------------------------------------------------------
# Task Routes (all require a valid JWT token)
# ---------------------------------------------------------------
@app.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([task.to_dict() for task in tasks]), 200


@app.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json(force=True, silent=True) or {}
    title = data.get("title")

    if not title:
        return jsonify({"error": "title is required"}), 400

    task = Task(
        title=title,
        description=data.get("description", ""),
        completed=False,
        user_id=user_id,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "task not found"}), 404

    data = request.get_json(force=True, silent=True) or {}
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.completed = data.get("completed", task.completed)
    db.session.commit()
    return jsonify(task.to_dict()), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "task deleted"}), 200


# ---------------------------------------------------------------
# Create the database tables on first run
# ---------------------------------------------------------------
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    import os
    # Render (and most hosts) assign a port dynamically via the PORT env variable.
    # This falls back to 5001 for local development.
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)
