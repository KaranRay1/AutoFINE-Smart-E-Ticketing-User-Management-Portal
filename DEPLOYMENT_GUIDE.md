# AutoFINE - Deployment Guide

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)

### Step 1: Install Dependencies
```bash
cd AutoFINE
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python init_database.py
```

### Step 3: Run the Application
```bash
python app.py
```

Or use the provided scripts:
- **Windows**: Double-click `start_server.bat`
- **PowerShell**: Run `.\start_server.ps1`

### Step 4: Access the Application
- Open your browser and navigate to: `http://localhost:5000`
- **Admin Login**: username=`admin`, password=`admin123`
- **Owner Login**: username=`john_doe`, password=`password123`

---

## 🌐 Production Deployment Options

### Option 1: Deploy on Heroku (Recommended for Quick Deployment)

#### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed
- Git installed

#### Steps:

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create a Procfile** (create in AutoFINE folder)
   ```
   web: gunicorn app:app
   ```

4. **Create runtime.txt** (specify Python version)
   ```
   python-3.12.0
   ```

5. **Update requirements.txt** (add gunicorn)
   ```
   gunicorn>=21.2.0
   ```

6. **Initialize Git Repository** (if not already)
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

7. **Create Heroku App**
   ```bash
   heroku create autofine-app
   ```

8. **Set Environment Variables**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key-here
   heroku config:set GEMINI_API_KEY=AIzaSyDhRmsMTyY6mRlZQylpk5OME1m-PDNrXiU
   ```

9. **Deploy**
   ```bash
   git push heroku main
   ```

10. **Open Your App**
    ```bash
    heroku open
    ```

---

### Option 2: Deploy on AWS (EC2 / Elastic Beanstalk)

#### Using AWS Elastic Beanstalk (Easier)

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB Application**
   ```bash
   cd AutoFINE
   eb init -p python-3.12 autofine-app
   ```

3. **Create Environment**
   ```bash
   eb create autofine-env
   ```

4. **Set Environment Variables**
   ```bash
   eb setenv SECRET_KEY=your-secret-key GEMINI_API_KEY=your-api-key
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

6. **Open Application**
   ```bash
   eb open
   ```

#### Using EC2 (Manual Setup)

1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 LTS
   - t2.micro (free tier) or larger
   - Configure security group: Allow HTTP (80), HTTPS (443), SSH (22)

2. **SSH into Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx git -y
   ```

4. **Clone/Upload Project**
   ```bash
   git clone your-repo-url
   # OR upload via SCP
   ```

5. **Setup Virtual Environment**
   ```bash
   cd AutoFINE
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

6. **Initialize Database**
   ```bash
   python init_database.py
   ```

7. **Create Gunicorn Service**
   ```bash
   sudo nano /etc/systemd/system/autofine.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=AutoFINE Gunicorn Service
   After=network.target

   [Service]
   User=ubuntu
   Group=www-data
   WorkingDirectory=/home/ubuntu/AutoFINE
   Environment="PATH=/home/ubuntu/AutoFINE/venv/bin"
   ExecStart=/home/ubuntu/AutoFINE/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app

   [Install]
   WantedBy=multi-user.target
   ```

8. **Start Service**
   ```bash
   sudo systemctl start autofine
   sudo systemctl enable autofine
   ```

9. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/autofine
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /static {
           alias /home/ubuntu/AutoFINE/static;
       }
   }
   ```

10. **Enable Site**
    ```bash
    sudo ln -s /etc/nginx/sites-available/autofine /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    ```

---

### Option 3: Deploy on DigitalOcean

1. **Create Droplet**
   - Choose Ubuntu 22.04
   - $6/month plan or higher

2. **Follow EC2 steps** (steps 2-10 from Option 2)

---

### Option 4: Deploy on Railway

1. **Sign up at Railway.app**

2. **Connect GitHub Repository**

3. **Add Environment Variables**
   - `SECRET_KEY`
   - `GEMINI_API_KEY`
   - `DATABASE_URL` (auto-provided)

4. **Deploy** (automatic on git push)

---

### Option 5: Deploy on Render

1. **Sign up at render.com**

2. **Create New Web Service**

3. **Connect Repository**

4. **Build Command**: `pip install -r requirements.txt && python init_database.py`

5. **Start Command**: `gunicorn app:app`

6. **Add Environment Variables**

7. **Deploy**

---

## 🔒 Security Checklist for Production

### 1. Change Secret Key
```python
# In app.py, change:
app.config['SECRET_KEY'] = 'your-very-long-random-secret-key-here'
# Or use environment variable:
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-key')
```

### 2. Use Environment Variables
Create a `.env` file (don't commit to git):
```
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
DATABASE_URL=sqlite:///autofine.db
```

Install python-dotenv:
```bash
pip install python-dotenv
```

Update app.py:
```python
from dotenv import load_dotenv
load_dotenv()
```

### 3. Use Production Database
- **PostgreSQL** (recommended):
  ```python
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/autofine')
  ```

- **MySQL**:
  ```python
  app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:pass@localhost/autofine'
  ```

### 4. Enable HTTPS
- Use Let's Encrypt (free SSL)
- Configure reverse proxy (Nginx/Apache)

### 5. Set Debug to False
```python
app.run(debug=False)  # Never use debug=True in production
```

### 6. Configure CORS (if needed)
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

---

## 📊 Database Migration (Production)

### Using Flask-Migrate

1. **Install Flask-Migrate**
   ```bash
   pip install flask-migrate
   ```

2. **Initialize Migrations**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

3. **For Future Changes**
   ```bash
   flask db migrate -m "Description"
   flask db upgrade
   ```

---

## 🔧 Performance Optimization

### 1. Use Gunicorn with Workers
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

### 2. Enable Caching
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

### 3. Use CDN for Static Files
- Upload static files to AWS S3 / CloudFront
- Or use a CDN service

### 4. Database Connection Pooling
```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600
}
```

---

## 📱 Mobile App Integration (Future)

The system is designed with RESTful APIs that can be consumed by:
- React Native apps
- Flutter apps
- Native iOS/Android apps

API endpoints are available at `/api/*` routes.

---

## 🆘 Troubleshooting

### Database Issues
```bash
# Reset database (development only)
rm autofine.db
python init_database.py
```

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill process or change port in app.py
```

### Import Errors
```bash
# Ensure you're in the correct directory
cd AutoFINE
python -m pip install -r requirements.txt --upgrade
```

---

## 📞 Support

For issues or questions:
1. Check the README.md
2. Review error logs
3. Check database connectivity
4. Verify environment variables

---

## 🎯 Quick Deployment Checklist

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Initialize database (`python init_database.py`)
- [ ] Set environment variables (SECRET_KEY, GEMINI_API_KEY)
- [ ] Change SECRET_KEY from default
- [ ] Set `debug=False` in production
- [ ] Use production database (PostgreSQL/MySQL)
- [ ] Configure HTTPS/SSL
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure firewall rules
- [ ] Set up monitoring/logging
- [ ] Test all endpoints
- [ ] Backup database regularly

---

**Happy Deploying! 🚀**
