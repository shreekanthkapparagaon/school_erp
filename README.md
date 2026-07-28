# School ERP

A modular, multi-tenant School ERP built with Django, designed for managing multiple schools through a feature-based subscription system. The project includes role-based access control, academic management, fee management, examination & results, document management, and a scalable architecture for future modules.

> **Current Release:** v2.1.0

---

## Features

* Multi-school (SaaS) architecture
* Role-based authentication and authorization
* Feature-based subscription plans
* Student management
* Teacher management
* Academic management
* Fee management
* Examination & Result management
* Document management
* Configurable school features
* Admin dashboard with Jazzmin
* Demo data generation utilities

---

## Tech Stack

* Python 3.14+
* Django 5
* SQLite (Development)
* PostgreSQL (Recommended Production)
* MySQL / MariaDB (Supported Production)
* uv
* HTML5
* CSS3
* JavaScript

---

## Prerequisites

* Python 3.14 or later
* uv

Install **uv** if it is not already installed:

```bash
pip install uv
```

---

# Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/shreekanthkapparagaon/school_erp.git
cd school_erp
```

## 2. Create a virtual environment

```bash
uv venv
```

## 3. Activate the virtual environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## Development Setup (SQLite)

Development uses SQLite by default.

Install dependencies:

```bash
uv sync
```

Create a `.env` file in the project root.

Example:

```env
DJANGO_SECRET_KEY=your-development-secret-key
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Apply migrations:

```bash
python manage.py migrate --settings=config.settings.dev
```

Run the development server:

```bash
python manage.py runserver --settings=config.settings.dev
```

---

## Production Setup (PostgreSQL / MySQL)

Production dependencies include:

* Gunicorn
* PostgreSQL driver (`psycopg`)
* MySQL/MariaDB driver (`mysqlclient`)

Install production dependencies:

```bash
uv sync --no-default-groups --group prod
```

Create a production environment file:

```env
DJANGO_SECRET_KEY=your-production-secret-key
DJANGO_ALLOWED_HOSTS=example.com,www.example.com

POSTGRES_DB=school_erp
POSTGRES_USER=schoolerp
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Use the production settings module:

```text
config.settings.prod
```

Run database migrations:

```bash
python manage.py migrate --settings=config.settings.prod
```

Run with Gunicorn:

```bash
gunicorn --env DJANGO_SETTINGS_MODULE=config.settings.prod config.wsgi:application
```

---

# Demo Data

Generate a complete demo environment including:

* Schools
* Users
* Subscription Plans
* Features
* Subscriptions
* Students
* Teachers
* Fees
* Results
* Demo credentials

Generate demo data:

```bash
python manage.py seed_demo_data
```

Delete demo data:

```bash
python manage.py delete_demo_data --yes
```

---

# Project Structure

```text
config/
├── settings/
│   ├── base.py
│   ├── dev.py
│   └── prod.py
│
apps/
├── accounts/
├── schools/
├── fees/
├── results/
├── document/
├── plans/
└── core/

static/
media/
templates/
```

---

# Profile

Authenticated users can access and manage their profile directly from the application sidebar after signing in.

---

# Roadmap

Planned modules include:

* Attendance Management
* Library Management
* Timetable Management
* Inventory Management
* Payroll Management
* Transport Management
* Hostel Management
* REST API
* Mobile Application

---

# License

This project is licensed under the MIT License.

---

# Notes

* Uses **uv** for dependency and virtual environment management.
* Development uses **SQLite** by default.
* Production supports **PostgreSQL** and **MySQL/MariaDB**.
* Gunicorn is included as a production dependency.
* Environment variables are managed using **python-dotenv**.
* Demo credentials are saved to `demo_credentials.txt`.
* Supports generating up to **50 demo schools**.
* Automatically creates plans, features, subscriptions, schools, users, fees, and examination results.
* `delete_demo_data --yes` removes all generated demo data.
