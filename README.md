# 📋 İş Takip SPA — Task Tracking Dashboard

[![Django](https://img.shields.io/badge/Django-6.0.3-092E20?logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Vue.js](https://img.shields.io/badge/Vue-3-4FC08D?logo=vue.js)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)](https://www.sqlite.org/)

> **İş Takip SPA** — Tek sayfa (SPA) yaklaşımıyla çalışan sade ve modern bir görev yönetim uygulaması.  
> A minimal single-page task management dashboard built with Django + Vue 3.

---

## ✨ Features

- **Single Page Application** — All operations within one screen (`/`)
- **Task Management** — Create, update, delete, and track tasks
- **Kanban-like Cards** — Visual task cards with priority, category, and status
- **Detail Drawer** — Click a task to view details in a side panel
- **Progress Logging** — Add progress notes to any task
- **Category Management** — Hierarchical categories with parent/child relationships
- **Role & Person Management** — Manage roles (Responsible, Worker) and assign people
- **Smart Filtering** — Filter by text, section, category, and completion status
- **Dashboard Statistics** — Total, open, completed, and overdue task counts
- **Responsive Design** — Works on desktop and mobile devices
- **Turkish UI** — Full Turkish language interface

---

## 🖼️ Screenshots

> _(Add screenshots here — see the `screenshots/` directory)_

| Dashboard | Task Detail | Category Management |
|-----------|-------------|-------------------|
| ![Dashboard](screenshots/dashboard.png) | ![Detail](screenshots/detail.png) | ![Categories](screenshots/categories.png) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pip (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/is_takip_django.git
cd is_takip_django

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your settings (optional for development)

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (optional, for admin panel)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

Visit **http://localhost:8000/** in your browser.

---

## 🌐 URLs

| Path | Description |
|------|-------------|
| `/` | SPA Task Dashboard (main) |
| `/admin/` | Django Admin Panel |
| `/api/bootstrap/` | Bootstrap API (loads all data) |
| `/api/tasks/` | Tasks API (GET/POST) |
| `/api/tasks/<id>/` | Task Detail API (GET/PATCH/DELETE) |
| `/api/tasks/<id>/logs/` | Task Progress Logs API (POST) |
| `/api/categories/` | Categories API (GET/POST) |
| `/api/categories/<id>/` | Category Detail API (PATCH/DELETE) |
| `/api/people/` | People API (GET/POST) |
| `/api/people/<id>/` | Person Detail API (PATCH/DELETE) |
| `/api/roles/` | Roles API (GET/POST) |
| `/api/roles/<id>/` | Role Detail API (PATCH/DELETE) |

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0.3 |
| **Frontend** | Vue 3 (CDN) + Vanilla JavaScript |
| **Database** | SQLite (default) |
| **CSS Framework** | Bootstrap 5.3 |
| **Styling** | Custom CSS (modern, minimal design) |
| **API** | Django JSON API (RESTful, no DRF) |

---

## 📁 Project Structure

```
is_takip_django/
│
├── config/               # Django project configuration
│   ├── settings.py       # Settings with env variable support
│   ├── urls.py           # Root URL configuration
│   ├── asgi.py           # ASGI application
│   └── wsgi.py           # WSGI application
│
├── tracker/              # Main application
│   ├── models.py         # Data models (Task, Category, Person, Role, ProgressLog)
│   ├── views.py          # API views and SPA shell
│   ├── urls.py           # App URL configuration
│   ├── forms.py          # Django forms
│   ├── admin.py          # Admin panel configuration
│   └── migrations/       # Database migrations
│
├── templates/            # HTML templates
│   ├── base.html         # Base template (legacy)
│   ├── partials/         # Reusable template partials
│   │   └── sidebar.html  # Sidebar navigation
│   └── tracker/
│       ├── spa.html      # Main SPA (Vue 3 application)
│       ├── task_list.html # Legacy task list
│       ├── task_form.html # Legacy task form
│       └── ...
│
├── static/               # Static files directory
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── LICENSE               # MIT License
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Django Secret Key — Generate for production!
DJANGO_SECRET_KEY=your-secret-key-here

# Set to False in production
DJANGO_DEBUG=True

# Comma-separated list of allowed hosts
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Generate a production secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 📸 Screenshots

To add screenshots:
1. Create a `screenshots/` directory
2. Capture screenshots of the dashboard, task detail, and category management
3. Name them `dashboard.png`, `detail.png`, and `categories.png`
4. Update the links in this README

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🗂️ GitHub Topics

`django` `task-management` `spa` `vuejs` `python` `tracker` `bootstrap` `sqlite` `django-vue` `single-page-application` `task-tracker`
