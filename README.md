# School ERP

A modular, multi-school ERP built with Django, featuring role-based access control, subscription plans, academic management, fee management, examination & results, and document management.

> Current Release: **v2.1.0**

---

## Features

- Multi-school management
- Student management
- Teacher management
- Academic management
- Fee management
- Examination & Results
- Document management
- Subscription plans & feature-based access
- Role-based authentication

---

## Tech Stack

- Python 3.13
- Django
- SQLite (default)
- PostgreSQL (recommended)
- uv
- HTML5
- CSS3
- JavaScript

---

## Prerequisites

- Python 3.13 or later
- uv

Install **uv** if you don't have it:

```bash
pip install uv
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/shreekanthkapparagaon/school_erp.git
cd school_erp
```

### 2. Create the virtual environment

```bash
uv venv
```

### 3. Activate the environment

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 4. Install project dependencies

```bash
uv sync
```

### 5. Configure development settings

Create a `.env` file or configure your settings in:

```text
config/settings/dev.py
```

### 6. Apply database migrations

```bash
python manage.py migrate --settings=config.settings.dev
```

### 7. Run the development server

```bash
python manage.py runserver --settings=config.settings.dev
```

---

## Demo Data

Generate a complete demo environment including schools, users, plans, subscriptions, fees, results, and demo credentials.

### Seed Demo Dataset

```bash
python manage.py seed_demo_data
```

### Delete Demo Data

Delete all demo data and reset the database.

```bash
python manage.py delete_demo_data --yes
```

---

## Profile

Authenticated users can access their profile from the application sidebar after logging in.

---

## Roadmap

Future modules planned for the project:

- Attendance Management
- Library Management
- Timetable Management
- Inventory Management
- Payroll
- REST API

---

## License

This project is licensed under the MIT License.

---

## Notes

- Uses **uv** for dependency and virtual environment management.
- SQLite is the default database for local development.
- PostgreSQL is recommended for production deployments.
- Demo credentials are written to `demo_credentials.txt`.
- Supports generating up to **50 demo schools**.
- Automatically creates plans, features, subscriptions, schools, users, fees, and results.
- `delete_demo_data --yes` removes all generated demo data.