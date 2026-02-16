# Deployment Guide

## Heroku Deployment

1. Install Heroku CLI and login:
```bash
heroku login
```

2. Create Heroku app:
```bash
heroku create your-app-name
```

3. Set environment variables:
```bash
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
```

4. Deploy:
```bash
git push heroku main
```

5. Initialize database:
```bash
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

Visit your app at: `https://your-app-name.herokuapp.com`

## Render Deployment

1. Create account at render.com
2. New Web Service → Connect your GitHub repo
3. Set environment variables:
   - `SECRET_KEY`: Generate random key
   - `PYTHON_VERSION`: 3.11.7
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`
6. Deploy

## PythonAnywhere

1. Upload files to PythonAnywhere
2. Create virtual environment:
```bash
mkvirtualenv --python=/usr/bin/python3.11 nptel
pip install -r requirements.txt
```

3. Configure WSGI file
4. Set SECRET_KEY in environment
5. Reload web app

## Environment Variables

Required:
- `SECRET_KEY`: Random secret key for sessions
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)

Generate SECRET_KEY:
```python
import secrets
print(secrets.token_hex(32))
```

## Post-Deployment

Visit `/admin/init_db` to initialize database with Week 1 data.
