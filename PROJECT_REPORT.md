# PROJECT PROGRESS REPORT

---

## AutoFINE: Smart E-Ticketing System Using Automatic License Plate Recognition (LPR)

**Prepared By:** Project Team  
**Institution:** [Your Institution Name]  
**Date:** January 2025  
**Report Type:** Progress Report (15-20 Pages)

---

# Table of Contents

1. [Project Title](#1-project-title)
2. [Introduction](#2-introduction)
3. [Objectives](#3-objectives)
4. [Methodology](#4-methodology)
5. [Results and Modules](#5-results-and-modules)
6. [Complete Status of the Project](#6-complete-status-of-the-project)
7. [References](#7-references)

---

# 1. Project Title

## AutoFINE: Smart E-Ticketing System Using Automatic License Plate Recognition (ALPR)

**Subtitle:** An AI-Powered Traffic Violation Detection and Challan Management System for Uttarakhand, India

---

# 2. Introduction

## 2.1 Background

With rapid urbanization and the exponential rise in the number of vehicles across India, monitoring traffic violations manually has become increasingly challenging. Traditional challan systems require traffic police to physically observe violations, record license plate numbers, and issue fines on the spot. This approach is labor-intensive, time-consuming, and highly prone to human error.

The Indian transport sector has witnessed tremendous growth over the past decade. According to government statistics, the total number of registered vehicles in India exceeds 295 million as of 2024, with Uttar Pradesh, Maharashtra, and Uttarakhand among the states with significant vehicle populations. Managing traffic compliance across such a vast scale demands technological intervention.

## 2.2 Problem Domain

The problem domain encompasses several critical issues faced by traffic enforcement agencies and citizens:

**2.2.1 Human Dependency and Limited Coverage**

Authorities must be physically present at intersections or checkpoints to record violations. It is impossible to monitor every street simultaneously, leading to unreported offenses. In urban areas with high traffic density, manual enforcement becomes impractical.

**2.2.2 Delayed or Missed Challan Generation**

Violators are often informed days or weeks after the offense, reducing the effectiveness of enforcement. In many cases, fines are not issued at all due to insufficient evidence or administrative bottlenecks.

**2.2.3 Data Inconsistency and Errors**

Handwritten challans may contain incorrect license plate numbers or fine amounts. Maintaining manual records makes verification difficult and unreliable. Disputes arise when citizens question the accuracy of recorded data.

**2.2.4 Lack of Transparency for Vehicle Owners**

Vehicle owners rarely have a centralized platform to check pending fines, due dates, or vehicle document expiry. This leads to surprise fines at checkpoints and disputes over unpaid challans.

**2.2.5 Scalability Issues**

As the number of vehicles continues to grow, manual enforcement cannot keep up, resulting in poor compliance with traffic laws. The system needs to scale automatically with increasing vehicular traffic.

## 2.3 Solution Overview

**AutoFINE** proposes an automated E-Challan system powered by Automatic License Plate Recognition (ALPR). Cameras installed on roads capture vehicle license plates; using computer vision and optical character recognition (OCR), the plate number is detected and matched against a centralized vehicle database. When a violation occurs, the system automatically generates a challan entry with details like fine amount, due date, and ticket type.

Vehicle owners can securely log into a web portal to view their vehicle details, including insurance or registration expiry dates, model number, pending fines, and payment status. A dashboard for traffic authorities enables real-time monitoring and management of violations.

---

# 3. Objectives

The main objectives and modules of the project are:

## 3.1 Primary Objectives

- **Automate License Plate Recognition using Computer Vision**
  - Implement image processing and OCR techniques to accurately detect and read vehicle license plates from images or video feeds.
  - Achieve acceptable accuracy under varying lighting and weather conditions.

- **Link Each License Plate to a Centralized Vehicle-Owner Database**
  - Maintain a structured database containing registration details, vehicle model, insurance expiry, and owner information.
  - Support Indian vehicle number formats (e.g., UK-XX-AA-0000 for Uttarakhand).

- **Generate and Update Challans Automatically for Detected Violations**
  - Eliminate manual data entry by creating violation records instantly when a traffic offense is identified.
  - Implement Uttarakhand Motor Vehicle Rules (2024-2026) for fine calculation.

- **Provide Real-Time Access to Vehicle and Challan Details via a Secure Web Portal**
  - Allow vehicle owners to log in and view fines, due dates, vehicle information, and payment status from any device.

- **Ensure Secure Authentication and Role-Based Access Control**
  - Implement user authentication for vehicle owners and an admin interface for traffic authorities.

- **Build an Admin Dashboard for Monitoring and Record Management**
  - Enable authorities to search vehicles, verify violations, and track payment status efficiently.

## 3.2 Secondary Objectives

- **Evaluate System Accuracy and Reliability under Varied Conditions**
  - Test the recognition module on images with different lighting, weather conditions, and license plate formats.

- **Design Modular Architecture for Future Upgrades**
  - Ensure the system can be easily extended to include online fine payment, SMS/email notifications, or integration with government transport databases.

## 3.3 Module Breakdown

1. **ALPR Module** – License plate detection and recognition
2. **Backend API Module** – Flask-based REST API and business logic
3. **Database Module** – SQLAlchemy ORM with User, Vehicle, Challan, Violation models
4. **Traffic Rules Engine** – Uttarakhand penalty calculation logic
5. **Admin Dashboard Module** – Violation processing, analytics, dataset management
6. **User Portal Module** – Owner dashboard, challan lookup, registration
7. **AI Integration Module** – Gemini API for news, insights, and notices
8. **Notification Module** – SMS and email services (mock/stub)

---

# 4. Methodology

## 4.1 Development Approach

The project follows an **Agile development methodology**, allowing iterative development and continuous testing. The core methodology involves:

1. **Requirement Analysis** – Understanding functional and non-functional requirements
2. **System Design** – Designing architecture, database schema, and user interfaces
3. **Module-wise Implementation** – Developing ALPR, backend APIs, and frontend as separate components
4. **Testing and Validation** – Testing ALPR accuracy and overall system functionality
5. **Deployment** – Deploying the prototype on a local server for demonstration

## 4.2 Technologies and Tools

| Component | Technology |
|-----------|------------|
| Backend | Python 3.10+, Flask 3.0, SQLAlchemy |
| Database | SQLite (development), PostgreSQL (production) |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 |
| ALPR | OpenCV, EasyOCR, NumPy, Pillow |
| AI/ML | Google Gemini API |
| Maps | Leaflet.js |
| Deployment | Gunicorn, Heroku/Render compatible |

## 4.3 Algorithms and Techniques

### 4.3.1 License Plate Recognition (ALPR)

The ALPR pipeline consists of the following stages:

**Stage 1: Image Preprocessing**

- **Grayscale Conversion:** Convert input image from BGR to grayscale for reduced computational complexity.
  \[ I_{gray} = 0.299R + 0.587G + 0.114B \]

- **Denoising:** Apply Non-Local Means Denoising to reduce noise while preserving edges.
  \[ \hat{I}(p) = \frac{1}{Z(p)} \sum_{q \in S(p)} w(p,q) \cdot I(q) \]
  where \( w(p,q) \) is the similarity weight between patches centered at \( p \) and \( q \).

- **Contrast Enhancement (CLAHE):** Contrast Limited Adaptive Histogram Equalization improves local contrast.
  \[ h'(i) = \min(h(i), T) \quad \text{where } T \text{ is clip limit} \]

- **Adaptive Thresholding:** Convert to binary image using Gaussian adaptive threshold.
  \[ T(x,y) = \mu(x,y) - C \]
  where \( \mu \) is local mean and \( C \) is constant.

**Stage 2: License Plate Region Detection**

- **Edge Detection:** Canny edge detector with thresholds (50, 150).
  \[ \text{Edge} = \nabla G * I \]

- **Morphological Operations:** Close operation with rectangular kernel (20×5) to connect edges and form plate-like regions.

- **Contour Analysis:** Filter contours by aspect ratio (2.0–5.0) and minimum area (1000 px²) to retain license plate candidates.

**Stage 3: Optical Character Recognition (OCR)**

- **EasyOCR:** Deep learning-based OCR model for English text.
- **Text Cleaning:** Regex-based cleanup, character replacement for common OCR errors (0→O, 1→I).
- **Confidence Scoring:** Each recognized text has an associated confidence value; highest confidence result is selected.

### 4.3.2 Traffic Rules Engine

The fine calculation follows Uttarakhand Motor Vehicle Rules 2024-2026:

**First Offense vs. Subsequent Offense Logic:**
\[ \text{prev\_count} = |\{c \in \text{Challans} : c.\text{vehicle\_id} = v \land c.\text{violation\_type} = t\}| \]
\[ \text{subsequent} = \text{prev\_count} > 0 \]

**Fine Calculation:**
- **No Helmet:** \( \text{fine} = 1000 \times 2^{\text{subsequent}} \) (₹1000 first, ₹2000 subsequent) + 3-month license suspension on subsequent
- **Drunk Driving:** \( \text{fine} = 0 \), Court mandatory (no online payment)
- **Signal Jumping:** \( \text{fine} = 1000 \) if first, \( 5000 \) if subsequent
- **Triple Riding:** \( \text{fine} = 1000 \)

### 4.3.3 Authentication and Security

- **Password Hashing:** Bcrypt with cost factor 12.
- **Session Management:** Flask session with server-side secret key.
- **Role-Based Access:** `user_type` field (owner/admin) controls route access.

### 4.3.4 AI Integration (Gemini API)

- **Traffic News Generation:** Prompt-based generation with JSON output parsing.
- **Predictive Insights:** City-wise traffic hotspot, peak time, and violation analysis.
- **Notice Summarization:** Extract key points from long traffic notices.

---

# 5. Results and Modules

## 5.1 Implemented Modules and Deliverables

### 5.1.1 ALPR Module (alpr_module/)

**Deliverables:**
- `license_plate_recognition.py` – Core OCR pipeline using EasyOCR and OpenCV
- Image preprocessing: grayscale, denoising, CLAHE, adaptive thresholding
- License plate region detection via contour analysis
- Text cleaning and formatting for Indian license plates
- Manual number plate entry option for fallback/override

**Results:**
- Supports both region-based and full-image OCR
- Handles multiple plate formats (UK-XX-AA-0000, PB-XX-XXXX)
- Confidence score returned for each recognition
- Batch processing support for multiple images

### 5.1.2 Backend and Database (app.py, models.py)

**Deliverables:**
- Flask application with 30+ routes
- SQLAlchemy models: User, Vehicle, Challan, Violation, Camera, Notice, Report, DriverLicense, Appeal, PaymentPlan
- RESTful API endpoints for challan processing, lookup, and analytics
- Server-Sent Events (SSE) for real-time challan updates

**Results:**
- Database schema supports multi-user, multi-vehicle, multi-challan scenarios
- Unique Identification Number (UIN) for each challan
- Foreign key relationships for data integrity

### 5.1.3 Traffic Rules Engine (traffic_rules.py)

**Deliverables:**
- `calculate_fine(violation_type, vehicle_id)` function
- First offense vs. subsequent offense logic
- Court-mandatory flag for drunk driving
- License suspension logic for repeated helmet violations

**Results:**
- Accurate fine calculation per Uttarakhand rules
- Integration with challan creation flow

### 5.1.4 Admin Dashboard (templates/admin/)

**Deliverables:**
- Dashboard with real-time statistics (total, unpaid, paid challans)
- Process Violation form with manual number plate entry and optional image upload
- Violation hotspots visualization
- AI Predictive Insights with city-wise traffic analysis
- Dataset Import (CSV upload from PC, URL import)
- All Vehicles and All Challans list views

**Results:**
- Full workflow for processing new violations
- Real-time updates via SSE
- Map integration (Leaflet.js) for traffic hotspots

### 5.1.5 User Portal (templates/owner/, templates/public/)

**Deliverables:**
- Owner dashboard with vehicle and challan overview
- Challan Lookup – public search by vehicle number, UIN, DL number, challan ID
- Traffic Notices – state/central government notices with AI refresh
- Report an Incident – form with email delivery

**Results:**
- Partial and case-insensitive search for challan lookup
- Gemini-powered notice updates

### 5.1.6 AI Integration (gemini_service.py)

**Deliverables:**
- Traffic news generation for home page
- Notice summarization
- Predictive insights (hotspots, peak times, common violations)
- City-specific traffic condition analysis

**Results:**
- Real-time AI-generated content
- JSON parsing for structured output

### 5.1.7 Supporting Services

**Deliverables:**
- `sms_service.py` – Mock SMS notification on challan generation
- `email_service.py` – SMTP-based email for incident reports
- `dataset_importer.py` – CSV import for vehicles, challans, violations

**Results:**
- Modular, configurable services
- Environment variable support for credentials

## 5.2 Data Sources and Datasets

- **Indian Traffic Violations** – CSV datasets for violation types
- **Government Open Data** – RTO/transport datasets (RS_Session_*)
- **Sample Data** – init_database.py seeds users, vehicles, challans for demo

## 5.3 User Interface

- Responsive design using Bootstrap 5
- Vehicle/Challan theme with light backgrounds (white, light blue, light yellow)
- Dark accents (navy blue, red) for important elements
- Login/Register pages with consistent button styling
- Home page with feature cards and Login/Register buttons

---

# 6. Complete Status of the Project

## 6.1 Overall Completion Status

**Important Note:** This project is **NOT YET COMPLETED**. The following reflects the current progress as a work-in-progress prototype.

### 6.2 Module-wise Completion Percentage

| Module | Description | Completion | Remarks |
|--------|-------------|------------|---------|
| ALPR Module | License plate recognition | **75%** | Core pipeline done; accuracy under varied conditions needs improvement |
| Backend API | Flask routes, business logic | **90%** | Major routes implemented; some edge cases pending |
| Database | Models, migrations | **95%** | Schema stable; production migration scripts pending |
| Traffic Rules Engine | Fine calculation | **85%** | Uttarakhand rules implemented; more violation types can be added |
| Admin Dashboard | Violation processing, analytics | **80%** | Main features done; advanced analytics partial |
| User Portal | Owner dashboard, lookup | **85%** | Lookup, notices, report done; payment flow pending |
| AI Integration | Gemini news, insights | **70%** | Basic integration done; robustness and error handling can improve |
| Notification Services | SMS, Email | **60%** | Mock/stub implementation; production integration pending |
| Payment Gateway | UKosh/UPI integration | **20%** | Placeholder only; not implemented |
| RTO/VAHAN Integration | Government database sync | **10%** | Not implemented; future scope |
| Deployment | Production hosting | **70%** | Procfile, requirements ready; tested on Render/Heroku |

### 6.3 Overall Project Completion: **Approximately 70%**

### 6.4 Completed Features

- User registration and login
- Admin and owner role-based access
- Manual and OCR-based violation processing
- Challan creation with UIN
- Challan lookup (vehicle, UIN, DL, ID)
- Traffic rules engine (Uttarakhand 2024-2026)
- Admin dashboard with real-time stats
- AI-powered news and insights
- Dataset import (CSV)
- Incident reporting with email
- Traffic notices with AI refresh
- Responsive UI with vehicle/challan theme

### 6.5 Pending/Incomplete Features

- Online payment gateway (UKosh, UPI)
- RTO/VAHAN database integration
- Live CCTV feed integration
- Production SMS gateway (Twilio)
- Virtual court / appeal workflow
- Blockchain-backed evidence (future scope)
- Mobile app (future scope)
- DigiLocker integration (future scope)

### 6.6 Known Limitations

- ALPR accuracy depends on image quality
- SQLite used for development; PostgreSQL recommended for production
- SMS and payment are mock implementations
- No live camera feed; uses uploaded images
- AI features require valid Gemini API key

---

# 7. References

1. Uttarakhand Motor Vehicles Rules, 2024-2026
2. Indian Motor Vehicles Act, 1988
3. OpenCV Documentation – https://docs.opencv.org/
4. EasyOCR – https://github.com/JaidedAI/EasyOCR
5. Flask Documentation – https://flask.palletsprojects.com/
6. Google Gemini API – https://ai.google.dev/
7. Parivahan Sewa – Government of India Transport Portal

---

# Appendix A: Project Structure

```
AutoFINE/
├── app.py                  # Main Flask application
├── models.py               # Database models
├── init_database.py        # Database initialization
├── traffic_rules.py        # Fine calculation logic
├── gemini_service.py       # AI integration
├── sms_service.py          # SMS notifications
├── email_service.py        # Email service
├── dataset_importer.py     # CSV import
├── alpr_module/            # License plate recognition
├── templates/              # HTML templates
├── static/                 # CSS, JS assets
├── data/                   # Sample datasets
├── requirements.txt        # Dependencies
├── Procfile                # Deployment config
└── README.md               # Documentation
```

---

# Appendix B: Sample Screenshots Description

- **Home Page:** AutoFINE branding, feature cards, Login/Register buttons
- **Admin Dashboard:** Stats cards, Process Violation form, Violation Hotspots, AI Insights, Dataset Import
- **Challan Lookup:** Search form, results table with UIN, vehicle, violation, amount, status
- **Owner Dashboard:** Vehicle list, challan summary

---

**End of Project Progress Report**

*This report documents the current state of the AutoFINE project as of January 2025. The project is under active development and subject to changes.*
