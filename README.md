# School ERP

A lightweight Django-based school management system with modular accounts, plans, fees, results, and contact workflows.

## Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # macOS / Linux
   .\.venv\Scripts\activate   # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` with your environment settings or configure `config/settings/dev.py`.
4. Run migrations:
   ```bash
   python manage.py migrate --settings=config.settings.dev
   ```

## Demo data seeding

Use the built-in demo seed command to generate schools, users, plans, subscriptions, fees, results, and demo credentials.

### Basic seed

```bash
python manage.py seed_demo_data --settings=config.settings.dev
```

### Seed with larger demo volume

```bash
python manage.py seed_demo_data --settings=config.settings.dev \
  --schools 20 \
  --students-per-school 120 \
  --teachers-per-school 20 \
  --classes-per-school 10 \
  --credentials-file demo_credentials.txt
```

### Reset and reseed demo data

This clears previously created demo plans, features, subscriptions, school demo data, and user accounts before seeding again.

```bash
python manage.py seed_demo_data --settings=config.settings.dev --reset --schools 10 --students-per-school 80
```

### Dry-run reset summary

```bash
python manage.py reset_demo_data --settings=config.settings.dev
```

### Confirmed reset

```bash
python manage.py reset_demo_data --settings=config.settings.dev --confirm
```

## Profile page

A new profile link is available in the sidebar when authenticated. It redirects to a profile detail page for the logged-in user.

## Notes

- Demo credentials are written to `demo_credentials.txt` by default.
- The seed command now supports bulk sizes up to 50 demo schools.
- Demo plans are created and assigned to schools with feature-based subscriptions.
