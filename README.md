# Task Manager REST API

A RESTful API for managing personal tasks, built with Flask, SQLAlchemy,
and JWT authentication. Each user can sign up, log in, and manage their
own private list of tasks.

🔗 **Live demo:** [add your deployed link here after deployment]

## Features

- User signup and login with hashed passwords (Werkzeug security)
- JWT-based authentication — tasks are private per user
- Full CRUD: Create, Read, Update, Delete tasks
- SQLite database (no external DB setup needed)

## Tech Stack

- **Python 3**
- **Flask** — web framework
- **Flask-SQLAlchemy** — ORM for database models
- **Flask-JWT-Extended** — token-based authentication
- **SQLite** — lightweight database

## API Endpoints

| Method | Endpoint          | Auth Required | Description                |
|--------|-------------------|----------------|----------------------------|
| POST   | `/signup`         | No             | Create a new user account  |
| POST   | `/login`          | No             | Log in, returns a JWT token|
| GET    | `/tasks`          | Yes            | Get all tasks for the user |
| POST   | `/tasks`          | Yes            | Create a new task          |
| PUT    | `/tasks/<id>`     | Yes            | Update an existing task    |
| DELETE | `/tasks/<id>`     | Yes            | Delete a task              |

## Example Usage (with curl)

```bash
# Sign up
curl -X POST http://127.0.0.1:5001/signup -H "Content-Type: application/json" -d '{"username":"sara","password":"test123"}'

# Log in (returns a token)
curl -X POST http://127.0.0.1:5001/login -H "Content-Type: application/json" -d '{"username":"sara","password":"test123"}'

# Create a task (replace <TOKEN> with the token from login)
curl -X POST http://127.0.0.1:5001/tasks -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" -d '{"title":"Learn Flask","description":"Build a project"}'

# Get all tasks
curl http://127.0.0.1:5001/tasks -H "Authorization: Bearer <TOKEN>"
```

You can also test this visually using **Postman** — import the endpoints
above as a collection.

## How to Run Locally

1. Clone this repository:
   ```
   git clone <your-repo-url>
   cd task-manager-api
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the app:
   ```
   python app.py
   ```

4. The API will be running at `http://127.0.0.1:5001`

## Deployment

Deployable for free on **Render** or **Railway** by connecting this
GitHub repository. Set the start command to `python app.py`.

## What I Learned

- Designing RESTful API endpoints following REST conventions
- Implementing secure authentication with password hashing and JWT tokens
- Structuring a Flask app with an ORM (SQLAlchemy) instead of raw SQL
- Enforcing per-user data isolation (users can only access their own data)

## Author

Sara Bano Qureshi — [LinkedIn](https://www.linkedin.com/in/sara-bano-qureshi-)
