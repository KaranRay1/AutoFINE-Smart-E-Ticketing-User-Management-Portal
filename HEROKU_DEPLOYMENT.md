# 🚀 Heroku Deployment Guide for AutoFINE

## Prerequisites

1. **Heroku Account** (Free tier available)
   - Sign up at: https://signup.heroku.com/

2. **Heroku CLI** (Command Line Interface)
   - Download: https://devcenter.heroku.com/articles/heroku-cli
   - Install and verify: `heroku --version`

3. **Git** (Version Control)
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

---

## Step-by-Step Deployment

### Step 1: Install Heroku CLI

1. Download Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli
2. Install it (follow the installer)
3. Verify installation:
   ```bash
   heroku --version
   ```

### Step 2: Login to Heroku

```bash
heroku login
```

This will open a browser window for authentication. Click "Log in" in the browser.

### Step 3: Navigate to Project Directory

```bash
cd "D:\Projects\E- Challan\AutoFINE"
```

### Step 4: Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit for Heroku deployment"
```

**Note**: If you already have a git repository, skip this step.

### Step 5: Create Heroku App

```bash
heroku create autofine-app
```

**Note**: Replace `autofine-app` with your desired app name (must be unique). Heroku will suggest a name if yours is taken.

You'll see output like:
```
Creating ⬢ autofine-app... done
https://autofine-app.herokuapp.com/ | https://git.heroku.com/autofine-app.git
```

### Step 6: Set Environment Variables

Set the secret key and Gemini API key:

```bash
heroku config:set SECRET_KEY=your-very-long-random-secret-key-here-change-this
heroku config:set GEMINI_API_KEY=AIzaSyDhRmsMTyY6mRlZQylpk5OME1m-PDNrXiU
```

**Important**: 
- Generate a strong SECRET_KEY (at least 32 characters, random)
- You can use: `python -c "import secrets; print(secrets.token_hex(32))"` to generate one

### Step 7: Add Heroku Postgres Database (Free Tier)

```bash
heroku addons:create heroku-postgresql:mini
```

This adds a free PostgreSQL database. The `DATABASE_URL` environment variable will be automatically set.

### Step 8: Deploy to Heroku

```bash
git push heroku main
```

**Note**: If your default branch is `master` instead of `main`, use:
```bash
git push heroku master
```

### Step 9: Initialize Database on Heroku

After deployment, initialize the database:

```bash
heroku run python init_database.py
```

This will create all tables and seed initial data.

### Step 10: Open Your App

```bash
heroku open
```

Or visit: `https://your-app-name.herokuapp.com`

---

## Post-Deployment Steps

### 1. Verify Deployment

- Open your app URL
- Test login with: `admin` / `admin123`
- Check all features are working

### 2. View Logs (if issues)

```bash
heroku logs --tail
```

### 3. Run Database Migrations (if needed)

```bash
heroku run python init_database.py
```

### 4. Scale Your App (if needed)

Free tier allows 1 dyno (web process). To scale:
```bash
heroku ps:scale web=1
```

---

## Updating Your App

After making changes:

```bash
git add .
git commit -m "Description of changes"
git push heroku main
```

Then restart if needed:
```bash
heroku restart
```

---

## Common Commands

### View App Info
```bash
heroku info
```

### View Environment Variables
```bash
heroku config
```

### Set Environment Variable
```bash
heroku config:set VARIABLE_NAME=value
```

### Remove Environment Variable
```bash
heroku config:unset VARIABLE_NAME
```

### View Logs
```bash
heroku logs --tail
```

### Run One-off Commands
```bash
heroku run python script.py
```

### Restart App
```bash
heroku restart
```

### Open App
```bash
heroku open
```

### Open Heroku Dashboard
```bash
heroku dashboard
```

---

## Troubleshooting

### Issue: "No app specified"
**Solution**: Make sure you're in the project directory and have run `heroku create`

### Issue: "Build failed"
**Solution**: 
- Check `requirements.txt` is correct
- Check `Procfile` exists and is correct
- View logs: `heroku logs --tail`

### Issue: "Application Error"
**Solution**:
- Check logs: `heroku logs --tail`
- Verify database is initialized: `heroku run python init_database.py`
- Check environment variables: `heroku config`

### Issue: "Database connection error"
**Solution**:
- Ensure Postgres addon is added: `heroku addons`
- Re-initialize database: `heroku run python init_database.py`

### Issue: "Module not found"
**Solution**:
- Check `requirements.txt` includes all dependencies
- Redeploy: `git push heroku main`

### Issue: "Port already in use" (local testing)
**Solution**: This shouldn't happen on Heroku, but if testing locally with Heroku CLI:
```bash
heroku local web
```

---

## Heroku Free Tier Limitations

1. **Dyno Hours**: 550 free hours/month (enough for 1 dyno running 24/7)
2. **Sleep Mode**: App sleeps after 30 minutes of inactivity (wakes on next request)
3. **Database**: 10,000 rows max on free Postgres
4. **Slug Size**: 500MB max
5. **Request Timeout**: 30 seconds

**Note**: For production, consider upgrading to paid plans.

---

## Security Checklist

- [x] Changed SECRET_KEY from default
- [x] Using environment variables for sensitive data
- [x] Database credentials managed by Heroku
- [ ] Set up custom domain (optional)
- [ ] Enable SSL (automatic on Heroku)
- [ ] Review and update default passwords

---

## Next Steps After Deployment

1. **Custom Domain** (Optional):
   ```bash
   heroku domains:add www.yourdomain.com
   ```

2. **Monitoring** (Optional):
   - Use Heroku's built-in metrics
   - Add New Relic or similar for advanced monitoring

3. **Backup Database**:
   ```bash
   heroku pg:backups:capture
   heroku pg:backups:download
   ```

4. **Set Up CI/CD** (Optional):
   - Connect GitHub repo
   - Enable automatic deploys

---

## Quick Reference

```bash
# Initial Setup
heroku login
heroku create app-name
heroku config:set SECRET_KEY=your-key
heroku config:set GEMINI_API_KEY=your-key
heroku addons:create heroku-postgresql:mini
git push heroku main
heroku run python init_database.py
heroku open

# Updates
git add .
git commit -m "Changes"
git push heroku main

# Troubleshooting
heroku logs --tail
heroku restart
heroku run python init_database.py
```

---

## Support

If you encounter issues:
1. Check logs: `heroku logs --tail`
2. Verify all files are committed: `git status`
3. Check Heroku status: https://status.heroku.com/
4. Review Heroku docs: https://devcenter.heroku.com/

---

**Your app will be live at: `https://your-app-name.herokuapp.com`** 🎉

Good luck with your deployment! 🚀
