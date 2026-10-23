# Feature Stories

Work top to bottom; each story builds on earlier ones and should be shippable on its own.

**Definition of done (every story):** all acceptance criteria met, tests added and passing, migrations committed.

Acceptance criteria are written as **Given / When / Then** scenarios. Each scenario should map to at least one automated test (or, for config/infra stories, a verifiable check).

The example domain is a **Task Tracker** (a small, familiar domain). Swap it for your own idea if you like; the story structure still applies.

---

## Epic 1 – Foundations

### S1. Base layout and navigation
As a visitor, I want a consistent header and footer so that the site feels cohesive.

**Acceptance criteria**
- **AC1** – Given any page extending `base.html`, when it renders, then it shows a nav, a content block and a footer.
- **AC2** – Given `static/css/site.css` exists, when a page loads, then the stylesheet is included via `{% static %}` and returns 200.
- **AC3** – Given a URL that does not exist, when I visit it, then a custom `404.html` is rendered with status 404.
- **AC4** – Given an unhandled server error (`DEBUG=False`), when it occurs, then a custom `500.html` is rendered with status 500.

### S2. Environment-based settings
As a developer, I want secrets and flags kept out of source control so that the app is safe to publish and configurable per environment.

**Acceptance criteria**
- **AC1** – Given `SECRET_KEY`, `DEBUG` and `ALLOWED_HOSTS` are set in the environment or `.env`, when Django starts, then it uses those values (via `python-decouple` or `django-environ`).
- **AC2** – Given a fresh clone, when I copy `.env.example` to `.env`, then the app starts without further edits.
- **AC3** – Given the repo, when I inspect version control, then `.env.example` is committed and `.env` is git-ignored.
- **AC4** – Given the README, when I read it, then every environment variable is documented with its purpose and an example value.

### S3. Health-check endpoint
As an operator, I want a `/health/` endpoint so that I can monitor whether the app is up.

**Acceptance criteria**
- **AC1** – Given the app is running, when I `GET /health/`, then the response is 200 with `Content-Type: application/json` and body `{"status": "ok"}`.
- **AC2** – Given the endpoint, when I request it without logging in, then it still responds (no auth required).
- **AC3** – Given the test suite, when it runs, then a test covers AC1.

---

## Epic 2 – Users

### S4. Sign up
As a visitor, I want to create an account so that I can use the app with my own data.

**Acceptance criteria**
- **AC1** – Given I am anonymous, when I `GET /accounts/signup/`, then I see a form with username and password fields (with confirmation).
- **AC2** – Given valid, unused credentials, when I submit the form, then a user is created, I am logged in, and I am redirected to the home page.
- **AC3** – Given a username that already exists, when I submit, then the form re-renders with an error and no user is created.
- **AC4** – Given a password that fails Django's validators (too short, too common, all numeric, similar to username) or mismatched confirmation, when I submit, then the form re-renders with the specific error.
- **AC5** – Given the test suite, when it runs, then tests cover success and each validation failure above.

### S5. Login and logout
As a user, I want to log in and out so that my account and data stay private.

**Acceptance criteria**
- **AC1** – Given `django.contrib.auth.urls` is included under `/accounts/`, when I visit `/accounts/login/`, then I see the login form rendered from `templates/registration/login.html`.
- **AC2** – Given valid credentials, when I log in, then I am redirected to the home page (or the `next` URL if provided).
- **AC3** – Given invalid credentials, when I log in, then the form re-renders with an error and I remain anonymous.
- **AC4** – Given I am logged in, when I log out (POST), then my session ends and I see the logged-out page or am redirected home.
- **AC5** – Given I am anonymous, when I view any page, then the nav shows Login and Sign up; given I am logged in, then it shows my username and Logout.

### S6. User profile
As a user, I want to edit my display name and bio so that my account feels personal.

**Acceptance criteria**
- **AC1** – Given the `Profile` model is one-to-one with `User`, when a new user is created, then a profile is created automatically via a signal.
- **AC2** – Given I am logged in, when I visit `/profile/`, then I see my display name and bio with an edit form.
- **AC3** – Given valid input, when I submit the edit form, then my profile is updated and I see the new values.
- **AC4** – Given I am anonymous, when I visit `/profile/`, then I am redirected to login.
- **AC5** – Given another user's profile, when I try to edit it, then access is denied (403/404) and nothing changes.

### S7. Password reset
As a user, I want to reset a forgotten password so that I can regain access to my account.

**Acceptance criteria**
- **AC1** – Given the dev settings, when a reset is requested, then the email is written to the console backend.
- **AC2** – Given a registered email, when I submit the reset request form, then I am redirected to the "email sent" page and exactly one email with a reset link is in `mail.outbox`.
- **AC3** – Given an unregistered email, when I submit the form, then I see the same "email sent" page and no email is sent (no account disclosure).
- **AC4** – Given a valid reset link, when I set a new valid password, then I can log in with it and the old password no longer works.
- **AC5** – Given the test suite, when it runs, then tests cover the request step (AC2, AC3).

---

## Epic 3 – Core feature: Tasks

### S8. Task model and admin
As an admin, I want to manage tasks in `/admin` so that I can inspect and correct data.

**Acceptance criteria**
- **AC1** – Given the `Task` model, when migrated, then it has: `title`, `description`, `status` (todo/doing/done), `due_date`, `owner` (FK User), `created_at`, `updated_at`.
- **AC2** – Given a new task created without a status, when saved, then `status` defaults to `todo`.
- **AC3** – Given `/admin/`, when I open Tasks, then the list shows `list_display` columns, offers `list_filter` (at least status) and `search_fields` (at least title).
- **AC4** – Given a task, when I call `str()` on it, then it returns its title.
- **AC5** – Given the test suite, when it runs, then model tests cover `__str__` and defaults.

### S9. List tasks
As a user, I want to see my tasks so that I know what I need to do.

**Acceptance criteria**
- **AC1** – Given I am logged in with tasks, when I visit `/tasks/`, then I see only tasks where I am the owner.
- **AC2** – Given another user's tasks exist, when I visit `/tasks/`, then none of them appear.
- **AC3** – Given I am anonymous, when I visit `/tasks/`, then I am redirected to login with `next=/tasks/`.
- **AC4** – Given I have no tasks, when I visit `/tasks/`, then I see an empty-state message.

### S10. Create a task
As a user, I want to add a task so that I can track new work.

**Acceptance criteria**
- **AC1** – Given I am logged in, when I visit `/tasks/new/`, then I see a `ModelForm` that does not expose the owner field.
- **AC2** – Given valid input, when I submit, then the task is saved with me as owner, I see a success message, and I am redirected to `/tasks/`.
- **AC3** – Given an empty title, when I submit, then the form re-renders with a "required" error and nothing is saved.
- **AC4** – Given a due date in the past, when I submit, then the form re-renders with an error and nothing is saved; a due date of today or later is accepted.
- **AC5** – Given I am anonymous, when I visit `/tasks/new/`, then I am redirected to login.

### S11. Task detail, edit, delete
As a user, I want to view, change and remove a task so that my list stays accurate.

**Acceptance criteria**
- **AC1** – Given my task, when I visit `/tasks/<id>/`, then I see its details.
- **AC2** – Given my task, when I submit valid changes at `/tasks/<id>/edit/`, then it is updated and I am redirected with a success message.
- **AC3** – Given my task, when I visit `/tasks/<id>/delete/`, then I see a confirmation page; when I confirm (POST), then the task is deleted and I am redirected to the list.
- **AC4** – Given a task owned by another user, when I request its detail, edit or delete URL, then the response is 404 and nothing changes.
- **AC5** – Given I am anonymous, when I request any of these URLs, then I am redirected to login.
- **AC6** – Given the test suite, when it runs, then tests cover each permission case above.

### S12. Quick status change
As a user, I want to mark a task done in one click so that updating progress is fast.

**Acceptance criteria**
- **AC1** – Given my task, when I POST to the status endpoint, then its status is toggled and I am redirected back to the list.
- **AC2** – Given a GET request to the endpoint, then it responds 405 and nothing changes.
- **AC3** – Given a POST without a valid CSRF token, then it is rejected with 403.
- **AC4** – Given a task owned by another user, when I POST, then the response is 404 and nothing changes.
- **AC5** – Given the list page, when it renders, then each task shows a button (inside a CSRF-protected form) that triggers the change.

### S13. Filter, search, sort
As a user, I want to find tasks quickly so that I can focus on what matters.

**Acceptance criteria**
- **AC1** – Given tasks in various statuses, when I choose a status filter, then only matching tasks are listed.
- **AC2** – Given a search term, when I submit it, then only tasks whose title contains it (case-insensitive) are listed.
- **AC3** – Given the sort control, when I sort by due date, then tasks are ordered by due date (ascending by default, with a way to reverse).
- **AC4** – Given any combination of filter, search and sort, when applied, then it is reflected in the query string, and reloading or sharing the URL reproduces the same view.
- **AC5** – Given filters are active, then the controls show their current values.

### S14. Pagination
As a user with many tasks, I want the list split into pages so that it loads quickly and stays readable.

**Acceptance criteria**
- **AC1** – Given more than 10 tasks, when I visit `/tasks/`, then at most 10 are shown with page links.
- **AC2** – Given filters, search or sort are active, when I change page, then those parameters are preserved.
- **AC3** – Given an out-of-range or invalid page number, when I request it, then the response is 404 (or the last page, consistently).
- **AC4** – Given 10 or fewer tasks, then no pagination controls are shown.

### S15. Categories / tags
As a user, I want to group tasks into categories so that I can organise related work.

**Acceptance criteria**
- **AC1** – Given the `Category` model, when created, then it belongs to a user, and names are unique per user.
- **AC2** – Given I am logged in, when I use the category views, then I can create, list, rename and delete my categories.
- **AC3** – Given another user's categories, then I cannot see, select, edit or delete them (404 for direct access).
- **AC4** – Given the task form, when I create or edit a task, then I can assign it one or more of my categories (per the FK/M2M choice).
- **AC5** – Given a category filter on `/tasks/`, when I select one, then only tasks in that category are listed.
- **AC6** – Given a category is deleted, then its tasks are not deleted.

---

## Epic 4 – Collaboration

### S16. Comments on tasks
As a user, I want to comment on a task so that I can record notes and discussion.

**Acceptance criteria**
- **AC1** – Given the `Comment` model, when migrated, then it has `task`, `author`, `body`, `created_at`.
- **AC2** – Given a task I can access, when I open its detail page, then I see its comments in chronological order with author and timestamp.
- **AC3** – Given a valid body, when I submit the comment form, then the comment is saved with me as author and shown on the page.
- **AC4** – Given an empty body, when I submit, then an error is shown and nothing is saved.
- **AC5** – Given a task I cannot access, then I cannot view or post comments on it.

### S17. Assign tasks to other users
As a task owner, I want to assign a task to another user so that responsibility is clear.

**Acceptance criteria**
- **AC1** – Given the `assignee` FK (nullable), when I edit my task, then I can choose another user or leave it unassigned.
- **AC2** – Given tasks assigned to me, when I visit the "Assigned to me" view, then I see exactly those tasks.
- **AC3** – Given I am the assignee, when I change a task's status, then it is saved.
- **AC4** – Given I am the assignee (not the owner), when I try to delete or edit other fields, then access is denied and nothing changes.
- **AC5** – Given I am neither owner nor assignee, then the task remains inaccessible (404).

### S18. Notifications by email
As an assignee, I want an email when a task is assigned to me so that I find out without checking the app.

**Acceptance criteria**
- **AC1** – Given a task is assigned (or reassigned) to a user with an email, when it is saved, then exactly one email is sent to that user containing the task title and a link.
- **AC2** – Given a task is saved with no assignee change, then no email is sent.
- **AC3** – Given a task is assigned to its own owner (self-assignment), then no email is sent.
- **AC4** – Given the dev settings, then emails go to the console backend.
- **AC5** – Given the implementation uses a signal or service function, when the tests run, then they assert on `mail.outbox` for AC1–AC3.

---

## Epic 5 – API

### S19. JSON API (read)
As an API client, I want to read tasks as JSON so that I can build other interfaces on the data.

**Acceptance criteria**
- **AC1** – Given Django REST Framework is installed, when an authenticated client requests `GET /api/tasks/`, then it receives 200 with a JSON list of that user's tasks.
- **AC2** – Given `GET /api/tasks/<id>/` for the user's own task, then it returns 200 with the task fields.
- **AC3** – Given another user's task, then detail returns 404 and the list excludes it.
- **AC4** – Given an unauthenticated request, then it returns 401/403.
- **AC5** – Given session or token auth is configured, then a client can authenticate using it.

### S20. JSON API (write)
As an API client, I want to create, change and delete tasks so that I can manage them programmatically.

**Acceptance criteria**
- **AC1** – Given valid data, when I `POST /api/tasks/`, then it returns 201 and the task is owned by me.
- **AC2** – Given invalid data (missing title, past due date), then it returns 400 with field errors and nothing is saved.
- **AC3** – Given my task, when I `PUT` or `PATCH` it, then it returns 200 and the changes are persisted; `PATCH` updates only the supplied fields.
- **AC4** – Given my task, when I `DELETE` it, then it returns 204 and it is removed.
- **AC5** – Given another user's task, then `PUT`, `PATCH` and `DELETE` return 404 and nothing changes.
- **AC6** – Given the test suite, when it runs, then `APIClient` tests cover each case above.

### S21. API docs
As an API consumer, I want interactive documentation so that I can learn and try the API without reading the source.

**Acceptance criteria**
- **AC1** – Given `drf-spectacular` is configured, when I request the schema endpoint, then it returns a valid OpenAPI document.
- **AC2** – Given I visit `/api/docs/`, then Swagger UI loads and lists all task endpoints.
- **AC3** – Given the schema is generated in CI or by command, then it completes without errors or unresolved warnings.

---

## Epic 6 – Quality and delivery

### S22. Test coverage and CI
As a maintainer, I want automated tests and coverage on every push so that regressions are caught early.

**Acceptance criteria**
- **AC1** – Given `coverage` is configured, when I run the test suite with coverage, then a report is produced.
- **AC2** – Given the coverage threshold is 85%, when coverage falls below it, then the run fails.
- **AC3** – Given a GitHub Actions workflow, when code is pushed, then tests run and the check passes or fails accordingly.

### S23. Linting and formatting
As a developer, I want consistent style enforced automatically so that reviews focus on substance.

**Acceptance criteria**
- **AC1** – Given `ruff` is configured in `pyproject.toml`, when I run lint and format commands, then they pass on the whole codebase.
- **AC2** – Given a pre-commit hook is installed, when I commit code that violates the rules, then the commit is blocked or auto-fixed.
- **AC3** – Given CI, then it runs the same lint and format checks.

### S24. PostgreSQL
As a developer, I want to run against PostgreSQL so that dev and production behave alike.

**Acceptance criteria**
- **AC1** – Given `DATABASE_URL` is set, when Django starts, then it connects to that database.
- **AC2** – Given `DATABASE_URL` is unset, then SQLite remains the default.
- **AC3** – Given `docker-compose.yml`, when I start the db service, then a Postgres instance is available and migrations apply cleanly.
- **AC4** – Given the test suite, then it passes on both SQLite and Postgres.

### S25. Dockerize
As an operator, I want a container image so that the app runs the same everywhere.

**Acceptance criteria**
- **AC1** – Given the `Dockerfile`, when built, then the image runs the app with gunicorn.
- **AC2** – Given `docker compose up`, then the app and db start and the app is reachable on the documented port.
- **AC3** – Given the running container, then static files are served via WhiteNoise (CSS loads with `DEBUG=False`).
- **AC4** – Given the README, then it documents how to build and run with Docker.

### S26. Background jobs
As a user, I want a daily digest of tasks due today so that I do not miss deadlines.

**Acceptance criteria**
- **AC1** – Given Celery and Redis are configured, when a worker starts, then it connects and registers the digest task.
- **AC2** – Given a user with tasks due today, when the digest runs, then they receive one email listing exactly those tasks.
- **AC3** – Given a user with no tasks due today, then no email is sent.
- **AC4** – Given a daily schedule (Celery beat), then the digest runs once per day at the configured time.
- **AC5** – Given the test suite, then the digest task is tested directly (eager mode) against `mail.outbox`.

### S27. Deploy
As an operator, I want the app deployed to a hosting platform so that real users can reach it.

**Acceptance criteria**
- **AC1** – Given a chosen platform (Render, Fly.io or Railway), when deployed, then the app is reachable at a public URL and `/health/` returns 200.
- **AC2** – Given production settings, then `DEBUG=False` and secrets come from environment variables.
- **AC3** – Given production settings, then secure cookies, HTTPS redirect and HSTS are enabled.
- **AC4** – Given `python manage.py check --deploy`, when run with production settings, then it reports no issues.
- **AC5** – Given the README, then it documents the deploy steps.

---

## Story template

```
### S<n>. <Title>
As a <role>, I want <capability> so that <benefit>.

**Acceptance criteria**
- **AC1** – Given <context>, when <action>, then <observable outcome>.
- **AC2** – Given <context>, when <action>, then <observable outcome>.
```
