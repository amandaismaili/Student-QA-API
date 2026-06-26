# Student Q&A Platform API

A RESTful Q&A API for university students, built with **FastAPI**, **PostgreSQL**, **SQLAlchemy** (async), and **JWT authentication**. Students can register, post questions, reply to others, and manage their own content. Includes database migrations with Alembic and a full test suite with pytest.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| Authentication | JWT (via python-jose) |
| Password Hashing | pwdlib |
| Validation | Pydantic v2 |
| Testing | pytest + anyio + httpx |
| Async Driver | asyncpg |

---

## Features

- User registration and login with JWT bearer token authentication
- Create, read, update, and delete questions
- Post and delete replies to questions
- Authorization — users can only edit or delete their own content
- Async database access throughout (SQLAlchemy async + asyncpg)
- Schema validation with Pydantic v2
- Database migrations managed with Alembic
- Test suite with isolated in-memory SQLite database (no pollution of real data)

---

## Project Structure

```
├── router/
│   ├── auth.py        # Registration, login, account management
│   └── section.py     # Questions and replies
├── alembic/           # Database migrations
├── test/
│   ├── conftest.py    # Fixtures, test client, helper functions
│   ├── test_post.py   # Question and reply endpoint tests
│   └── test_users.py  # User registration and auth tests
├── main.py            # App entry point, router registration
├── models.py          # SQLAlchemy ORM models
├── schemas.py         # Pydantic request/response schemas
├── database.py        # Async engine and session setup
├── authen.py          # JWT creation, verification, current user dependency
└── config.py          # Pydantic settings loaded from .env
```

---

## API Endpoints

### Account (`/account`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/account/register` | Register a new user | No |
| POST | `/account/login` | Login and receive JWT token | No |
| GET | `/account/me` | Get current authenticated user | Yes |
| DELETE | `/account/delete/` | Delete own account | Yes |
| PUT | `/account/search/{user_id}` | Update account details | Yes |

### Questions & Replies (`/section`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/section` | Get all questions | No |
| POST | `/section/questions` | Create a new question | Yes |
| GET | `/section/search/{id}` | Get a question by ID | No |
| PUT | `/section/search/{id}` | Full update of a question | Yes |
| PATCH | `/section/search/{id}` | Partial update of a question | Yes |
| DELETE | `/section/question/{id}` | Delete a question | Yes |
| POST | `/section/reply` | Post a reply to a question | Yes |
| DELETE | `/section/reply/{id}` | Delete a reply | Yes |

---

## Running Locally

### Prerequisites
- Python 3.11+
- PostgreSQL running locally

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/amandaismaili/Student-QA-API.git
   cd Student-QA-API
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:
   ```
   DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/dbname
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

7. Open the interactive API docs at `http://localhost:8000/docs`

---

## Running Tests

Tests run against an isolated in-memory SQLite database — no setup needed beyond installing dependencies.

```bash
pytest -v
```

---

## Authentication

This API uses JWT bearer token authentication. To access protected endpoints:

1. Register a user via `POST /account/register`
2. Login via `POST /account/login` to receive an access token
3. Include the token in the `Authorization` header:
   ```
   Authorization: Bearer <your_token>
   ```
