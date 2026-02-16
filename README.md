# NPTEL Software Testing Solutions Hub

Modern Flask web application for NPTEL Software Testing (noc26_cs59) assignment solutions with user authentication and progress tracking.

## Features

- User registration & authentication
- Personal progress tracking per week
- Interactive answer reveal system
- Modern glassmorphism UI
- Fully responsive design
- Weekly assignment management

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000/admin/init_db` to initialize database, then go to `http://localhost:5000`

## Adding New Weeks

Use `add_week.py`:
```bash
python add_week.py
```

## Tech Stack

Flask, SQLAlchemy, Flask-Login, SQLite

## Course Info

**Course**: Software Testing | **Code**: noc26_cs59 | **Platform**: NPTEL
