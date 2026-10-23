# Django Starter

A minimal Django project to grow feature by feature. See [STORIES.md](STORIES.md) for the backlog.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Test
```bash
python manage.py test
```

## Layout
- `config/` – project settings and root URLs
- `core/` – first app (home page); add new apps with `python manage.py startapp <name>`
- `templates/` – project-wide templates (`base.html`)
- `static/` – project-wide static files

## Working a story
1. Create a branch per story. 2. Write a failing test. 3. Implement. 4. Run `python manage.py test`. 5. Tick the acceptance criteria in STORIES.md.
