# Task Management Web Application

## 📌 Project Overview
This project is a **Task Management Web Application** designed to help users organize and manage their daily tasks through a simple and user-friendly web interface. The system allows users to **register**, **log in**, and access a personalized **dashboard** where they can create, view, update, and delete tasks. The application demonstrates core software engineering concepts including requirement analysis, system design, testing, version control, CI/CD pipelines, and deployment.

The project was developed as part of a software engineering course to apply theoretical concepts in a practical, end-to-end software development process.

---

## 🧩 Features
- User registration and login
- User dashboard
- Create new tasks
- View all tasks
- Update existing tasks
- Delete tasks
- Responsive frontend using Bootstrap
- Automated testing with Pytest
- Continuous Integration using GitHub Actions
- Cloud deployment

---

## 🛠️ Technology Stack

### Backend
- Python
- Flask
- Flask-SQLAlchemy
- SQLite

### Frontend
- HTML
- CSS
- Bootstrap
- JavaScript (Fetch API)

### DevOps & Tools
- Git & GitHub
- GitHub Actions (CI)
- Pytest
- Gunicorn
- Render (Deployment)

---

## 📂 Project Structure
task-management-system/
│
├── app/
│ ├── init.py
│ ├── models.py
│ ├── routes.py
│
├── templates/
│ └── index.html
│
├── static/
│ └── style.css
│
├── tests/
│ └── test_tasks.py
│
├── docs/
│ ├── specifications.md
│ ├── requirements.md
│ ├── test_cases.md
│ └── diagrams/
│ ├── use_case.puml
│ ├── class_diagram.puml
│ └── sequence_diagram.puml
│
├── .github/
│ └── workflows/
│ └── ci.yml
│
├── backlog.md
├── scrum_meetings.md
├── requirements.txt
├── run.py
└── README.md


---

## 🧪 Testing
Automated tests are written using **Pytest** and cover the main CRUD operations of the task management system.

To run tests locally:
```bash
python -m pytest

---

## 🧪 Testing
Automated tests are written using **Pytest** and cover the main CRUD operations of the task management system.

To run tests locally:
```bash
python -m pytest

🔄 Continuous Integration (CI)

📋 Documentation

All project documentation is available in the docs/ folder, including:

Software Specifications

Functional and Non-Functional Requirements

Test Cases

UML Diagrams (Use Case, Class, Sequence)

📊 Agile & Scrum Artifacts

The project follows Agile practices and includes:

Product Backlog (backlog.md)

Scrum meeting summaries (scrum_meetings.md)

GitHub Issues for task tracking

GitHub Project Board for Scrum workflow

Pull Requests for code integration
