# Customer_Management_System


A Django web app for managing customers and their support tickets. It has three kinds of users (admin, agent and customer), a ticket workflow with status rules and history, customer follow-ups, and an admin dashboard with charts.

## Features

- **Role-based access**
  - **Admin** (superuser): manages customers, agents and all tickets, and sees the dashboard.
  - **Agent** (staff user): sees only the tickets assigned to them and the customers behind those tickets.
  - **Customer** (regular user): sees their own profile, tickets and follow-ups.
- **Tickets**: create, edit, delete, search by title or description, filter by status, and paginate. Each ticket has a category (technical, billing, general, complaint), a priority (low to urgent) and an assigned agent.
- **Status workflow**: agents can only make valid status changes, for example `open → in_progress → resolved → closed`. The rules are in `project/Validators.py`.
- **Audit trail**: every status change is stored in the ticket's status history. Assignments and other changes are logged in a ticket activity feed.
- **Team comments**: admins and agents can post threaded internal comments on a ticket.
- **Customers**: admins can add, edit, delete, search and filter customers by status. Each customer also has a detail page.
- **Follow-ups**: staff can schedule follow-ups for a customer, optionally linked to a ticket and assigned to an agent.
- **Admin dashboard**: pie charts of tickets by status, customers by status and tickets by assignee, plus recent status changes.
- **Authentication**: login, logout, password change and password reset.

## Tech stack

- Python 3.12
- Django 5.2
- MySQL 8 (through PyMySQL and mysqlclient)
- Matplotlib (dashboard charts)
- Docker and Docker Compose

## Project structure

```
.
├── manage.py
├── settings.py            # Django settings (DJANGO_SETTINGS_MODULE = "settings")
├── urls.py                # Root URL configuration
├── Dockerfile
├── Docker-compose.yml
├── requirements.txt
└── project/               # The Django app
    ├── Models/            # Customer, Follow_up, Ticket, TicketStatusHistory,
    │                      # TicketActivity, TicketComment
    ├── Controller/        # Views: Admin, Agent, Customer, Register, Ticket
    ├── Routes/            # URL patterns for each controller
    ├── Forms/             # Django forms
    ├── Templates/         # HTML templates (Admin, Agent, Customer, Register, Ticket)
    ├── static/            # CSS for each section
    ├── migrations/
    ├── middleware.py      # Adds no-cache headers to every response
    └── Validators.py      # Ticket status transition rules
```

## Getting started

### Option 1: Docker (recommended)

This starts the app and a MySQL 8 database together.

```bash
docker compose -f Docker-compose.yml up --build
```

In a second terminal, create the tables and an admin account:

```bash
docker compose -f Docker-compose.yml exec web python manage.py migrate
docker compose -f Docker-compose.yml exec web python manage.py createsuperuser
```

The app is then available at <http://localhost:8000>.

### Option 2: Run locally

You need Python 3.12 and a running MySQL server.

1. Create the database:

   ```sql
   CREATE DATABASE newdb;
   ```

2. Create a virtual environment and install the dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt matplotlib
   ```

   `mysqlclient` needs the MySQL client development headers on your system. On Debian or Ubuntu these are `default-libmysqlclient-dev`, `build-essential` and `pkg-config`.

3. Set the database connection (optional, see the defaults below), then migrate and run:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

### Configuration

The database is configured with environment variables:

| Variable      | Default     |
|---------------|-------------|
| `DB_NAME`     | `newdb`     |
| `DB_USER`     | `root`      |
| `DB_PASSWORD` | `root@1234` |
| `DB_HOST`     | `localhost` |

The MySQL port is fixed at `3306`. Password reset emails are printed to the console by default (`EMAIL_BACKEND` is the console backend). The SMTP settings are in `settings.py`, commented out.

## Usage

| URL | Who | What |
|-----|-----|------|
| `/` or `/login/` | Everyone | Log in. Admins and agents go to the dashboard, customers go to their profile. |
| `/signup/` | Logged-in users | Create a new customer account. |
| `/password-change/` | Logged-in users | Change your password. |
| `/tickets/` | Everyone | Ticket list, scoped to your role. |
| `/customers/` | Admin | Manage customers. |
| `/customers/me/` | Customer | Your profile, tickets and follow-ups. |
| `/customers/mycustomers/` | Agent | Customers behind your assigned tickets. |
| `/agents/` | Admin | List and create agents. |
| `/admin-panel/` | Admin | Dashboard with charts and status history. |
| `/admin/` | Admin | Built-in Django admin. |

A typical setup is to create a superuser, log in, add agents under `/agents/`, then add customers. Customers can then log in, raise tickets, and an admin assigns each ticket to an agent.

## Security notes

This project is set up for development. Before deploying it:

- Replace the hard-coded `SECRET_KEY` and set `DEBUG = False` and `ALLOWED_HOSTS` in `settings.py`.
- Change the default database password in `settings.py` and `Docker-compose.yml`.
- Customers created by an admin are given the initial password `test@123`. Ask them to change it at first login.

## License

No license has been specified.