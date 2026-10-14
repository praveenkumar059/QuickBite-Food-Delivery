# QuickBite – Food Delivery Management System

A beginner-friendly Django application for browsing food, managing a session cart, placing cash-on-delivery orders, and reviewing personal order history. Staff manage food and order statuses through Django admin. This is a local learning project, not a deployed commercial service.

## Features and stack

- Built-in User registration, hashed passwords, login, POST logout, and protected customer pages.
- Available-food menu, category labels, detail pages, local SVG illustrations with a fallback.
- Session cart: add, set quantity (increase/decrease), remove, Decimal subtotals.
- Validated delivery address/contact, server-calculated prices, atomic order creation, unique checkout token.
- Historical names and unit prices, personal order history and ownership-checked details.
- Staff admin food CRUD, order search/filter, and manual status updates.

Python **3.12 or 3.14** recommended; supported range 3.10–3.14. Django **5.2 LTS**, dependency range `>=5.2.13,<5.3`; verification uses the version recorded in `docs/COMPLETION.md`. Install the latest compatible patch. SQLite is included with Python. HTML, Django templates, CSS, Bootstrap **5.3.3** (CDN). Django installs its transitive dependencies, including timezone data on Windows. No Pillow is needed because images are static assets, not uploads.

Official compatibility: [Django 5.2 release notes](https://docs.djangoproject.com/en/5.2/releases/5.2/). Supported releases: [Django downloads](https://www.djangoproject.com/download/).

## File structure

```text
QuickBite/
  manage.py, requirements.txt, README.md, .gitignore, FILE_MANIFEST.md
  config/      settings, root URLs, WSGI and ASGI entry points
  orders/      models, forms, cart helper, views, URLs, admin, tests
    migrations/0001_initial.py
    management/commands/seed_menu.py
  templates/   base, authentication and order workflow pages
  static/      css/style.css, img/food.svg
  docs/        learning, interview, testing and completion guides
```

See [FILE_MANIFEST.md](FILE_MANIFEST.md) for the exact file inventory. The database is generated locally; it is not shipped. There is no media directory because this version uses static images.

## Windows PowerShell and VS Code: step by step

1. Install Python from python.org with Python added to PATH, and install VS Code with its Python extension. Open PowerShell and check:

   ```powershell
   py --version
   py -m pip --version
   ```

   Successful output shows a supported Python version and pip location. If `py` fails, try `python`. If Windows opens the Store or reports an inaccessible alias, disable the Python App Execution Alias in Windows settings or use your actual installed Python executable with `& 'C:\path\to\python.exe'`.

2. Download and extract the source ZIP. The ZIP already contains the project and app; **do not run startproject or startapp over these files**. For example, extract to `E:\python\QuickBite`. In PowerShell:

   ```powershell
   Set-Location E:\python\QuickBite
   Get-ChildItem
   code .
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

   Run every remaining Python command in this folder, where `manage.py` exists. Activation usually adds `(.venv)` to the prompt. In VS Code, use “Python: Select Interpreter” to select `.venv\Scripts\python.exe`. If activation is blocked, use `.\.venv\Scripts\python.exe` instead of `python` for every command; no policy change is needed. Installation should finish with “Successfully installed” or “Requirement already satisfied”.

3. Settings, URLs, templates, and admin registrations are already configured. Create database tables and sample menu:

   ```powershell
   python manage.py check
   python manage.py migrate
   python manage.py seed_menu
   python manage.py createsuperuser
   python manage.py test
   python manage.py runserver
   ```

   `check` should report no issues; migrations print `OK`; seed prints `Sample menu ready`; superuser prompts for your own username, optional email and password (password typing is invisible). Tests should print `OK`. Server output includes `http://127.0.0.1:8000/`. Keep that terminal running. Stop with Ctrl+C.

4. Open [the local website](http://127.0.0.1:8000/) in your browser. Register a customer, add food, change quantities, checkout with a real-format test address and dummy contact number, then review the saved order. Open [Django admin](http://127.0.0.1:8000/admin/) and use the superuser credentials. Add/change/delete food and update an order's status. Refresh the customer order to see that change. Create another customer to test isolation.

The equivalent commands used to create an empty Django scaffold are `django-admin startproject config .` and `python manage.py startapp orders`; they are educational background only. This download supplies their completed equivalents.

## Migrations and schema changes

`migrate` applies the included schema migration plus Django's authentication/session migrations. After you intentionally edit models:

```powershell
python manage.py makemigrations orders
python manage.py migrate
python manage.py check
python manage.py test
```

Commit new migration files. Do not delete migration files or a database containing valuable orders to resolve errors. First read the error, use `python manage.py showmigrations`, and check that you are in the correct folder and environment.

## Images, styling and configuration

All menu items initially use the included `static/img/food.svg` illustration. Add your own licensed image under `static/img/`, then change the admin image field to its relative path, e.g. `img/dosa.jpg`. The field is a static path, not an upload or external URL. Missing images fall back to the SVG. Bootstrap loads from a CDN; internet is needed for its full styling. Custom CSS and images are local. No Bootstrap JavaScript is required.

The local development secret key is randomly generated at startup and never committed. Restarting may invalidate old sessions; log in again. Optionally set a private stable key in the terminal:

```powershell
$env:DJANGO_SECRET_KEY = 'your-own-long-random-development-value'
python manage.py runserver
```

Do not commit an actual key or this terminal value. `.env` files are ignored but **not automatically loaded**. Production requires a private stable key, `DJANGO_DEBUG=0`, configured allowed hosts, HTTPS, static-file hosting and a proper server/security review. Secure cookie/HTTPS settings activate with DEBUG off. The development server is for local use.

## Troubleshooting

| Symptom | What to check |
|---|---|
| Python not found / Store alias | `py --version`; actual Python executable; PATH and App Execution Aliases |
| No module named django | Activate the correct venv; `python -m pip install -r requirements.txt`; VS Code interpreter |
| manage.py not found | `Get-Location`; change to the extracted QuickBite directory |
| no such table | Run `python manage.py migrate` with the same interpreter/settings |
| TemplateDoesNotExist | Check `templates/` files and settings `DIRS`; preserve the extracted folder structure |
| NoReverseMatch | Compare the named URL and arguments in `orders/urls.py`; detail routes need `pk` |
| Missing CSS/image | Check static relative path; `python manage.py findstatic css/style.css`; DEBUG must be on locally; check CDN access |
| Port already in use | `python manage.py runserver 8001`, then visit port 8001 |
| CSRF failure | Reload the form; allow cookies; use the same host throughout; do not disable CSRF |
| SQLite database locked | Avoid concurrent heavy writes; stop duplicate servers and retry; SQLite is a learning/small-use database |

## Tests and learning

Run `python manage.py test` for automated workflow/security checks. Read [testing checklist](docs/TESTING.md) for manual browser checks and [actual verification record](docs/COMPLETION.md) for what was executed. [Learning guide](docs/LEARNING_GUIDE.md) explains each file and Django concepts; [interview preparation](docs/INTERVIEW.md) provides spoken answers.

## Screenshots

No screenshots are fabricated or included. Run the application, create dummy sample orders, and capture actual menu, cart, checkout, personal orders, and admin pages using Win+Shift+S. Save under `docs/screenshots/`, avoiding personal contact details and credentials. Then add Markdown image links here, e.g. `![Menu](docs/screenshots/menu.png)`.

## Limitations and future enhancements

Cash on delivery is a displayed payment arrangement; there is no payment collection or settlement system. No payment gateway, GPS tracking, delivery app or REST API. Status choices are Pending → Confirmed → Preparing → Out for Delivery → Delivered as a staff convention; this version does not enforce transition order and permits staff corrections. No cancellation feature. No inventory reservations, delivery fees, taxes, email verification, password reset workflow, pagination or production login rate limiting. A simultaneous menu edit can affect the submitted total; prices are re-read at submission and the saved order is authoritative. The token prevents ordinary duplicate checkout posts, but SQLite concurrent-write contention may require retrying; this is not a high-volume checkout system. Cart is tied to the authenticated session; logout clears it. Future work could add uploaded images, enforced status transitions, pagination, and carefully scoped payment integration.

## Public GitHub submission

Suggested repository: **quickbite-django**. Description: “Beginner-friendly Django food ordering app with a session cart, secure customer order history, and staff admin.” Create an empty GitHub repository without an initial README, then run inside QuickBite:

```powershell
git init
git branch -M main
git add .
git status
git diff --cached --stat
git ls-files
git check-ignore db.sqlite3 .venv .env
git commit -m "Build QuickBite Django food ordering project"
git remote add origin https://github.com/YOUR_USERNAME/quickbite-django.git
git push -u origin main
```

Before committing, review `git ls-files`: no database, venv, .env, passwords or customer details should appear. `git check-ignore` should list ignored paths; for a directory, use an existing file inside it if necessary. Never put a GitHub token into a source file or remote URL; use Git's credential manager/browser authentication. If a sensitive file was already tracked, `git rm --cached PATH` stops future tracking but does not erase history; rotate leaked secrets and clean history before making the repo public. After pushing, inspect the GitHub file list and compare it with the manifest. Download a fresh clone and run setup to verify reproducibility.
