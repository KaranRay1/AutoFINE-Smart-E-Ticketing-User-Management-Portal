# AutoFINE - Smart E-Challan System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**AutoFINE** is an AI-powered E-Challan (Traffic Violation Ticketing) System for Uttarakhand, India. It features automatic license plate recognition, real-time challan management, and a comprehensive dashboard for both vehicle owners and traffic authorities.

## Features

- **Automatic License Plate Recognition (ALPR)** - AI-powered vehicle detection
- **Real-time Challan Management** - Process violations instantly
- **Admin Dashboard** - Monitor violations, vehicles, and analytics
- **User Portal** - Vehicle owners can check challans and pay fines
- **Challan Lookup** - Public search by vehicle number, UIN, or DL number
- **Traffic Rules Engine** - Uttarakhand 2024-2026 penalty calculations
- **AI Insights** - Gemini-powered traffic predictions and news
- **SMS Notifications** - Alert vehicle owners on challan generation

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **AI/ML:** OpenCV, EasyOCR, Google Gemini API
- **Maps:** Leaflet.js

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/AutoFINE.git
cd AutoFINE
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Create a `.env` file:
```env
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
DATABASE_URL=sqlite:///autofine.db
```

### 5. Initialize Database
```bash
python init_database.py
```

### 6. Run the Application
```bash
python app.py
```

### 7. Access the Application
Open browser: **http://localhost:5000**

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |

## Project Structure

```
AutoFINE/
├── app.py                  # Main Flask application
├── models.py               # Database models
├── init_database.py        # Database initialization
├── requirements.txt        # Python dependencies
├── Procfile               # Heroku deployment
├── runtime.txt            # Python version
│
├── alpr_module/           # License plate recognition
│   ├── __init__.py
│   └── license_plate_recognition.py
│
├── static/                # Static files
│   ├── css/
│   │   └── vehicle-challan-theme.css
│   └── js/
│       ├── advanced-features.js
│       ├── gemini-news.js
│       └── realtime.js
│
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── challans.html
│   │   └── vehicles.html
│   ├── owner/
│   │   └── dashboard.html
│   └── public/
│       ├── lookup.html
│       ├── notices.html
│       └── report.html
│
├── traffic_rules.py       # Uttarakhand traffic rules
├── gemini_service.py      # AI service integration
├── sms_service.py         # SMS notifications
├── email_service.py       # Email service
└── dataset_importer.py    # Data import utilities
```

## Deployment

### Deploy to Render (Recommended - Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create New Web Service
4. Connect your GitHub repo
5. Set environment variables
6. Deploy!

### Deploy to Heroku

```bash
heroku login
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
heroku config:set GEMINI_API_KEY=your-api-key
git push heroku main
heroku run python init_database.py
heroku open
```

### Deploy to Railway

1. Push to GitHub
2. Go to [railway.app](https://railway.app)
3. New Project → Deploy from GitHub
4. Add environment variables
5. Deploy

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/login` | GET/POST | User login |
| `/register` | GET/POST | User registration |
| `/admin/dashboard` | GET | Admin dashboard |
| `/admin/process_violation` | POST | Process new violation |
| `/public/lookup` | GET | Challan search |
| `/api/realtime/challans` | GET | SSE real-time updates |

## Screenshots

### Home Page
- Clean, professional interface
- Login/Register buttons
- Feature highlights

### Admin Dashboard
- Real-time statistics
- Process violations
- AI insights
- Dataset management

### Challan Lookup
- Search by vehicle number
- Search by UIN
- Search by DL number

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Contact

- **Project:** AutoFINE E-Challan System
- **Location:** Uttarakhand, India

---

**Made with ❤️ for Smart Traffic Management**
