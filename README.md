# Vacationly - Family Vacation Planner

A modern, glassmorphic vacation planning application designed for families to coordinate time off, track remaining days, and plan trips together.

## Features
- **Liquid Glass UI:** Modern macOS-inspired aesthetic with backdrop blurs and translucency.
- **Smart Time Tracking:** Automatically excludes weekends and public holidays from allowance deductions.
- **Visual Planning:** Elegant Gantt chart for family-wide availability overview.
- **Family Management:** Add/Remove family members, define regional holiday calendars, and manage yearly time off allowances.
- **HTMX Powered:** Smooth, SPA-like interactions without the complexity of modern JS frameworks.

## Tech Stack
- **Backend:** Python (Flask / WSGI)
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** Jinja2, HTMX, Tailwind CSS (via CDN), Frappe Gantt
- **Logic:** `holidays` library for regional public holiday support

## Running Locally

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (for ultra-fast package management)

### Setup
1. Clone the repository and enter the directory.
2. Create virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```
3. Seed the database with demo data:
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   python3 seed.py
   ```

### Start the Server
```bash
uv run flask --app app.main:app run --debug
```

### Access
Open [http://localhost:8000](http://localhost:8000) in your browser.

### Demo Credentials:
- Email: `demo@example.com`
- Password: `demo123`

## How It Works
The system uses the `holidays` library to fetch official holidays for supported countries (CH, MX, DE, US, etc.). When planning time off, the system iterates through each day and only deducts from the balance if the day is:
1. An available day (defined per family member, e.g., 5 or 6 days/week based on their typical schedule).
2. Not an official public holiday in the family member's country/region.

This allows families to:
- Plan joint vacations while seeing everyone's availability
- Track individual time off for work, school, or personal days
- Automatically exclude non-work/school days from allowance calculations
- See remaining time off at a glance for each family member
