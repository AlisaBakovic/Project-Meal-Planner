# Meal Planner App

Fullstack web application for managing meal plans where trainers can create and manage plans for their clients.

---

## Features

* User authentication with JWT
* Role-based system (trainer and client)
* Create and view plans
* Protected routes using tokens
* React frontend with Vite

---

## Tech Stack

Backend:

* Python
* Flask
* SQLAlchemy
* JWT authentication

Frontend:

* React (Vite)
* JavaScript
* Fetch API

---

## Setup

### Backend

1. Create virtual environment:

```
python -m venv venv
```

2. Activate environment:

```
source venv/bin/activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Run server:

```
python app.py
```

---

### Frontend

1. Navigate to frontend folder:

```
cd meal-planner-frontend
```

2. Install dependencies:

```
npm install
```

3. Start development server:

```
npm run dev
```

4. Open in browser:

```
http://localhost:5173
```

---

## Authentication

* Login endpoint:

```
POST /login
```

* Token is stored in localStorage
* Protected routes require:

```
Authorization: Bearer <token>
```

---

## API Endpoints

Auth:

* POST /login

Plans:

* GET /plans
* POST /plans

---

## Application Flow

1. User logs in and receives a token
2. Token is used for authenticated requests
3. Backend validates token
4. Data is returned based on user role

---

## Future Improvements

* Client management (GET /clients)
* Invite system
* Food database integration
* UI improvements
* Edit and delete plans

---

## Notes

* Backend is the source of truth
* Frontend handles UI and interactions
* JWT is used for authentication

---

## Author

Alisa Bakovic
Fullstack Developer (Learning Project)
https://github.com/AlisaBakovic
