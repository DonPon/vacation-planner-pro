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
- Username: `demo@example.com`
- Password: `demo123`

## Deploying behind a path prefix

The app builds all links with Flask's `url_for`, so it can run under a path such as
`https://example.com/vacation-planner/`.

Set these environment variables for the production process:

| Variable | Purpose |
| --- | --- |
| `APP_PREFIX` | Path prefix, e.g. `/vacation-planner`. Leave unset for local root hosting. |
| `SECRET_KEY` | Long random secret (required in production; do not use the dev default). |
| `SESSION_COOKIE_NAME` | Unique cookie name so other Flask apps on the same domain do not clash (defaults to `vacationplanner_session`). |
| `DATABASE_URL` | Absolute SQLite URL, e.g. `sqlite:////var/lib/vacation-planner/app.db`. Defaults to `app.db` next to `wsgi.py`. |
| `PREFIX_FROM_HEADER` | Set to `1` only if your proxy strips the prefix and sends `X-Forwarded-Prefix`. |

Run with gunicorn:

```bash
uv pip install gunicorn
APP_PREFIX=/vacation-planner SECRET_KEY="$(openssl rand -hex 32)" \
DATABASE_URL=sqlite:////var/lib/vacation-planner/app.db \
gunicorn --workers 2 --bind 127.0.0.1:8001 wsgi:application
```

### Proxy option A (default): forward the full path

nginx:

```nginx
location /vacation-planner/ {
    proxy_pass http://127.0.0.1:8001;   # no trailing slash
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

`DispatcherMiddleware` in `wsgi.py` strips `/vacation-planner` before Flask sees the request,
and generated URLs include the prefix automatically.

### Proxy option B: proxy strips the prefix

If your existing setup uses `proxy_pass http://127.0.0.1:8001/;` (trailing slash), set
`PREFIX_FROM_HEADER=1` and send the prefix as a header:

```nginx
location /vacation-planner/ {
    proxy_pass http://127.0.0.1:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /vacation-planner;
}
```

Do not set both options at once.

> Never run `seed.py` against the production database: it drops all tables first.

## How It Works
The system uses the `holidays` library to fetch official holidays for supported countries (CH, MX, DE, US, etc.). When planning time off, the system iterates through each day and only deducts from the balance if the day is:
1. An available day (defined per family member, e.g., 5 or 6 days/week based on their typical schedule).
2. Not an official public holiday in the family member's country/region.

This allows families to:
- Plan joint vacations while seeing everyone's availability
- Track individual time off for work, school, or personal days
- Automatically exclude non-work/school days from allowance calculations
- See remaining time off at a glance for each family member
