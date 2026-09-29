# Bidirectional Student–RM Externship Tracker (POC)

Django POC where students and Relationship Managers (RMs) share a live log of
externship-site communications, and students can update placement status
(including offers) that appears on the RM dashboard.

## Features

- **Students** log calls, interviews, emails, and other site communications
- **RMs** add notes/communications for a student (visible to that student)
- **Status updates** — students mark offer received / accepted / placed, etc.
- **RM dashboard** highlights offer alerts and shows roster status at a glance
- UI color palette aligned with the HarperRand **Student Portal**
  (navy `#001a39`, yellow `#feae2c`, body `#f3f5f7`, Roboto)

## Quick start

```bash
cd "Bidirectional student–RM externship tracker"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open http://127.0.0.1:8000/login/

### Demo accounts (password: `demo1234`)

| Role    | Username   |
|---------|------------|
| RM      | `rm1`      |
| Student | `student1` |
| Student | `student2` (has offer received) |
| Student | `student3` |

## Try the flow

1. Sign in as **student2** → see offer status and communications
2. Sign in as **rm1** → offer alert on dashboard for Jordan Patel
3. As **student1**, log a new interview → visible on RM student detail
4. As **rm1**, open a student → “Add note for student” → visible on student dashboard

## Project layout

```
accounts/     Custom User (student / RM roles, RM assignment)
tracker/      Communication + ExternshipStatus models, views, seed command
templates/    Dashboards and forms
static/css/   Student Portal–aligned styles
```
