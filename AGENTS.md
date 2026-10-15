# Working notes for this repository (Base44 sandbox)

Django 5.1 project (`PP/settings.py`) with two apps: `testing` (the main site —
fish stock, money stock and their logs, plus the staff-only pages) and
`register` (account signup). Templates are server-rendered.

## Running it here

```bash
docker compose -f docker-compose.base44.yml up -d --build
```

Web entry point: <http://localhost:3000/> (host port 3000). It is a single
service that runs the Django **development** server from the bind-mounted
source (`runserver 0.0.0.0:3000`), so source edits hot-reload via Django's
StatReloader; no rebuild is needed for code changes. `DEBUG=True` (from
`.env.base44-defaults`) is what makes the dev server serve the static files
under `/static/`.

## Non-obvious things worth knowing

- **No database service.** The app uses the SQLite file `db.sqlite3` at the repo
  root, which is committed and therefore shared live with the sandbox through
  the bind mount. Data written in the preview persists between sessions and is
  part of the working tree. `python manage.py migrate --noinput` runs on every
  container start (a no-op once applied). Never delete that file.
- **`SECRET_KEY`.** `PP/settings.py` reads it with django-environ. A real value
  is delivered from `/run/base44/app.env` (declared in `.base44/environment.json`
  as `requiredAtBoot`); the generated development placeholder there must be
  replaced with a real secret before any real deployment.
  In the **sandbox preview only** settings fall back to a built-in development
  key when no `SECRET_KEY` has been delivered yet, so a fresh environment no
  longer restart-loops with
  `django.core.exceptions.ImproperlyConfigured: Set the SECRET_KEY environment
  variable` (the failure that kept the preview from starting). The fallback is
  gated on `BASE44_PREVIEW_MODE == "1"` — see the sandbox section below. With the
  flag unset the app still refuses to start without `SECRET_KEY`, exactly as
  before. `.env.base44-defaults` holds only non-secret dev defaults and is listed
  *before* `/run/base44/app.env` so real values win.
- **Django's default login URL is broken in this project** (pre-existing): the
  project maps `django.contrib.auth.urls` at `/` and `LOGIN_URL` is not set, so
  an anonymous visit to a `@login_required` page redirects to
  `/accounts/login/`, which 404s. The nav links to `/login/`, which works, so
  this only affects people who open `/fishlist/` or `/balance/` directly while
  logged out. Left as-is; set `LOGIN_URL = "/login/"` if it should be fixed.
- `testing/forms.py` builds `ModelChoiceField` querysets at import time, so
  adding fish/spaces requires the page to be re-rendered (a normal POST does
  that). Nothing extra is needed in the sandbox.

## Sandbox-only overrides (gated on `BASE44_PREVIEW_MODE`)

Both overrides below apply only while the platform sets
`BASE44_PREVIEW_MODE == "1"` (it never appears in the repo's own defaults). With
the flag unset or any other value, the settings behave exactly as before.

### 1. `SECRET_KEY` fallback

`SECRET_KEY` is read with `env("SECRET_KEY", default=None)`. When it is missing
and the flag is `"1"`, settings use a built-in development key instead of
raising:

```python
if os.environ.get("BASE44_PREVIEW_MODE") == "1":
    SECRET_KEY = "base44-sandbox-preview-only-insecure-key"
else:
    raise ImproperlyConfigured("Set the SECRET_KEY environment variable")
```

Why: a fresh environment starts with an empty `/run/base44/app.env`, so the dev
server died with `ImproperlyConfigured: Set the SECRET_KEY environment variable`
and the container restart-looped — the preview never started. A delivered
`SECRET_KEY` is read first and always wins, so the real value is never masked,
and with the flag unset the original exception is raised unchanged (verified with
`env -u SECRET_KEY python manage.py check`). This is a preview convenience only:
never rely on it for a real deployment.

### 2. CSRF trusted origin

`PP/settings.py` appends the public preview origin to `CSRF_TRUSTED_ORIGINS`
only when `BASE44_PREVIEW_MODE == "1"` **and** `BASE44_PUBLIC_HOST_SUFFIX` is
set:

```python
CSRF_TRUSTED_ORIGINS = [f"https://3000-{os.environ['BASE44_PUBLIC_HOST_SUFFIX']}"]
```

Why: the preview proxy terminates TLS and forwards the request with the sandbox
host, while the browser sends its own public `Origin`. Django ≥ 4.0 verifies the
`Origin` on unsafe methods, so **every form POST 403'd** ("Origin checking
failed") — login, registration and the add/remove stock forms were all dead in
the preview. The trusted origin is computed from the environment (never
hardcoded, since the suffix changes per environment). A wildcard
(`https://*.suffix`) does *not* work here: the preview host is
`3000-<suffix>`, where the port is part of the leftmost label, so the wildcard
label match never applies.

With `BASE44_PREVIEW_MODE` unset or any value other than `"1"`, no trusted
origins are added and the settings behave exactly as before. CSRF protection
itself is untouched — only this one preview origin is trusted.

## Verifying the app works

Anonymous: `/` (landing page), `/about/`, `/login/`, `/register/`.

Staff-only, need an account with `is_staff` (`/fishlist/`, `/balance/`); the
committed database already contains staff users. To exercise one, create your
own staff user, drive `/login/`, then **delete that user and its sessions again**
— the SQLite file is real, shared data.
