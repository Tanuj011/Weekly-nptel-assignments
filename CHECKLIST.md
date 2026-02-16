# Production Deployment Checklist

## Before Deployment

- [ ] Set SECRET_KEY environment variable (never use default!)
- [ ] Test locally: `python app.py`
- [ ] Verify all dependencies in requirements.txt
- [ ] Check .gitignore includes `*.db`, `.env`, `__pycache__`
- [ ] Remove any test/debug code

## Deploy

- [ ] Push to GitHub
- [ ] Deploy to hosting platform (Heroku/Render/PythonAnywhere)
- [ ] Set environment variables on platform
- [ ] Initialize database: visit `/admin/init_db`
- [ ] Test registration and login
- [ ] Verify Week 1 data loads correctly

## Post-Deployment

- [ ] Create your admin account
- [ ] Test all features
- [ ] Add Week 2 when ready: `python add_week.py`
- [ ] Share URL with students

## Weekly Updates

When new assignment releases:
1. Run `python add_week.py` locally
2. Or add directly via Python shell on server
3. Set status to 'active'
4. Students see it immediately

## Security

- [ ] SECRET_KEY is random and secure
- [ ] Database backups enabled
- [ ] HTTPS enabled (automatic on most platforms)
- [ ] No sensitive data in git repo
