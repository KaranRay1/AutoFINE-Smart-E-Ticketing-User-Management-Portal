# Deployment Guide for AutoFINE

## Option 1: Deploy to Render.com (Recommended - FREE)

### Step 1: Push to GitHub
```bash
cd AutoFINE
git init
git add .
git commit -m "Initial commit - AutoFINE E-Challan System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AutoFINE.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign up
2. Click **New +** → **Web Service**
3. Connect your GitHub account
4. Select your **AutoFINE** repository
5. Configure:
   - **Name:** autofine
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. Add Environment Variables:
   - `SECRET_KEY` = (generate random string)
   - `GEMINI_API_KEY` = (your Gemini API key)
   - `DATABASE_URL` = (Render provides this automatically)
7. Click **Create Web Service**

Your app will be live at: `https://autofine.onrender.com`

---

## Option 2: Deploy to Railway.app (FREE tier available)

1. Go to [railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Add environment variables in Settings
5. Railway will auto-deploy!

---

## Option 3: Deploy to Heroku

### Prerequisites
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- Heroku account

### Steps
```bash
# Login to Heroku
heroku login

# Create app
heroku create autofine-echallan

# Add PostgreSQL database
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set GEMINI_API_KEY=your-gemini-api-key

# Deploy
git push heroku main

# Initialize database
heroku run python init_database.py

# Open app
heroku open
```

---

## Option 4: Deploy to PythonAnywhere (FREE)

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Create free account
3. Go to **Web** tab → **Add a new web app**
4. Choose **Flask** and **Python 3.10**
5. Upload your files via **Files** tab
6. Set up virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 autofine
   pip install -r requirements.txt
   ```
7. Configure WSGI file to point to your app
8. Reload the web app

---

## Environment Variables Required

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key | Yes |
| `DATABASE_URL` | Database connection string | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `SMTP_HOST` | Email SMTP host | Optional |
| `SMTP_USER` | Email username | Optional |
| `SMTP_PASS` | Email password | Optional |

---

## After Deployment

1. Visit your deployed URL
2. Login with: `admin` / `admin123`
3. Go to Admin Dashboard
4. Import datasets if needed
5. Start processing violations!

---

## Troubleshooting

### Database Issues
```bash
# Heroku
heroku run python init_database.py

# Local
python init_database.py
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Port Issues
The app automatically uses the `PORT` environment variable set by hosting platforms.
