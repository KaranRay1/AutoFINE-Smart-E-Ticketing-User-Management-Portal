"""
AutoFINE: Smart E-Ticketing System Using LPR
Main Flask Application
"""

import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import json
import time
import threading
import random
from sms_service import send_sms
from traffic_rules import calculate_fine
import uuid


app = Flask(__name__)
# Use environment variable for secret key, fallback to default for development
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'autofine-secret-key-2024-change-in-production')
# Try SQLite first for easier setup, can switch to MySQL later
# For MySQL: 'mysql+pymysql://username:password@localhost/autofine_db'
# For SQLite (default):
# Use Heroku Postgres if available, otherwise SQLite
database_url = os.environ.get('DATABASE_URL', 'sqlite:///autofine.db')
# Heroku Postgres uses postgres:// but SQLAlchemy needs postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
from models import db
db.init_app(app)
bcrypt = Bcrypt(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

# Import models after db initialization
from models import User, Vehicle, Challan, Violation, Camera, Notice, Report, DriverLicense, Appeal, PaymentPlan

# Import Gemini service
from gemini_service import generate_traffic_news, generate_notice_summary, get_traffic_rules_explanation, generate_appeal_guidance, get_predictive_insights, get_gemini_model

# Routes
@app.route('/')
def index():
    """Home page with Gemini-generated news"""
    # Get real-time traffic news from Gemini
    try:
        news = generate_traffic_news()
    except Exception as e:
        print(f"Error generating news: {e}")
        news = {
            "title": "Welcome to AutoFINE",
            "content": "Smart E-Ticketing System for Traffic Management",
            "type": "info",
            "timestamp": datetime.now().isoformat()
        }
    
    return render_template('index.html', news=news)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'owner')
        
        user = User.query.filter_by(username=username, user_type=user_type).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type
            
            if user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('owner_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration (for vehicle owners)"""
    if request.method == 'POST':
        try:
            from sqlalchemy.exc import IntegrityError
        except ImportError:
            IntegrityError = Exception

        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''
        phone = (request.form.get('phone') or '').strip()
        dl_number = (request.form.get('dl_number') or '').strip().upper() or None

        if not username or not email or not password or not phone:
            flash('Please fill all required fields (Username, Email, Phone, Password).', 'error')
            return render_template('register.html')
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[1]:
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different username.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please use a different email.', 'error')
            return render_template('register.html')
        if dl_number and User.query.filter_by(dl_number=dl_number).first():
            flash('DL Number already exists. Please check your DL number.', 'error')
            return render_template('register.html')
        
        # Create new user
        try:
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(
                username=username,
                email=email,
                phone=phone,
                dl_number=dl_number,
                password_hash=password_hash,
                user_type='owner'
            )
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            if 'UNIQUE' in error_msg or 'duplicate' in error_msg.lower():
                flash('Registration failed: Username, email, or DL number already exists.', 'error')
            else:
                flash(f'Registration failed: {error_msg}', 'error')
            return render_template('register.html')
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/owner/dashboard')
def owner_dashboard():
    """Vehicle owner dashboard"""
    if 'user_id' not in session or session.get('user_type') != 'owner':
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    vehicles = Vehicle.query.filter_by(owner_id=user_id).all()
    
    # Get all challans for user's vehicles
    vehicle_ids = [v.id for v in vehicles]
    challans = Challan.query.filter(Challan.vehicle_id.in_(vehicle_ids)).order_by(Challan.created_at.desc()).all()
    
    return render_template('owner/dashboard.html', vehicles=vehicles, challans=challans)

@app.route('/owner/vehicle/<int:vehicle_id>')
def owner_vehicle_detail(vehicle_id):
    """Vehicle detail page for owner"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Verify ownership
    if vehicle.owner_id != session['user_id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('owner_dashboard'))
    
    challans = Challan.query.filter_by(vehicle_id=vehicle_id).order_by(Challan.created_at.desc()).all()
    
    # Check for overdue challans
    today = datetime.now().date()
    for challan in challans:
        if challan.status != 'Paid' and challan.due_date and challan.due_date < today:
            challan._is_overdue = True
        else:
            challan._is_overdue = False
    
    return render_template('owner/vehicle_detail.html', vehicle=vehicle, challans=challans, today=today)


@app.route('/challan/<int:challan_id>/pay')
def challan_pay_page(challan_id):
    """Dedicated payment page for a challan: details, Razorpay button, QR code."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    challan = Challan.query.get_or_404(challan_id)
    if challan.status == 'Paid':
        flash('This challan is already paid.', 'info')
        return redirect(url_for('owner_dashboard'))
    if challan.status == 'Court' or challan.violation_type == 'Drunk Driving':
        flash('This challan cannot be paid online. Please visit the court.', 'error')
        return redirect(url_for('owner_dashboard'))
    is_admin = session.get('user_type') == 'admin'
    if not is_admin:
        vehicles = Vehicle.query.filter_by(owner_id=session['user_id']).all()
        if challan.vehicle_id not in [v.id for v in vehicles]:
            flash('You do not have permission to pay this challan.', 'error')
            return redirect(url_for('owner_dashboard'))
    payment_page_url = request.url
    qr_base64 = None
    try:
        import qrcode
        import io
        import base64
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(payment_page_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        qr_base64 = base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"QR generation failed: {e}")
    return render_template('owner/pay_challan.html', challan=challan, qr_base64=qr_base64, payment_page_url=payment_page_url)

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    # Statistics
    total_vehicles = Vehicle.query.count()
    total_challans = Challan.query.count()
    unpaid_challans = Challan.query.filter_by(status='Unpaid').count()
    paid_challans = Challan.query.filter_by(status='Paid').count()
    
    # Recent challans
    recent_challans = Challan.query.order_by(Challan.created_at.desc()).limit(10).all()
    
    stats = {
        'total_vehicles': total_vehicles,
        'total_challans': total_challans,
        'unpaid_challans': unpaid_challans,
        'paid_challans': paid_challans
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_challans=recent_challans)

@app.route('/admin/vehicles')
def admin_vehicles():
    """Admin - View all vehicles"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    if search:
        vehicles = Vehicle.query.filter(
            (Vehicle.license_number.like(f'%{search}%')) |
            (Vehicle.model.like(f'%{search}%'))
        ).all()
    else:
        vehicles = Vehicle.query.all()
    
    # Assign random colors to vehicles missing color
    try:
        color_pool = ["Red","Blue","Black","White","Silver","Green","Yellow","Orange","Grey","Maroon","Teal","Purple","Brown"]
        changed = False
        for v in vehicles:
            if not v.color or v.color.strip() == '':
                v.color = random.choice(color_pool)
                changed = True
        if changed:
            db.session.commit()
    except Exception:
        pass
    
    return render_template('admin/vehicles.html', vehicles=vehicles, search=search)

@app.route('/admin/challans')
def admin_challans():
    """Admin - View all challans"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Challan.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search:
        query = query.join(Vehicle).filter(Vehicle.license_number.like(f'%{search}%'))
    
    challans = query.order_by(Challan.created_at.desc()).all()
    view_challans = []
    for ch in challans:
        try:
            lic = ch.vehicle.license_number if ch.vehicle else 'N/A'
        except Exception:
            lic = 'N/A'
        try:
            created_str = ch.created_at.strftime('%Y-%m-%d %H:%M') if ch.created_at else 'N/A'
        except Exception:
            created_str = 'N/A'
        try:
            due_str = ch.due_date.strftime('%Y-%m-%d') if ch.due_date else 'N/A'
        except Exception:
            due_str = 'N/A'
        view_challans.append({
            'id': ch.id,
            'license_number': lic,
            'violation_type': ch.violation_type,
            'location': ch.location or 'N/A',
            'fine_amount': ch.fine_amount,
            'due_date': due_str,
            'status': ch.status,
            'created_at': created_str
        })
    
    try:
        return render_template('admin/challans.html', challans=view_challans, status_filter=status_filter, search=search)
    except Exception as e:
        return f"Template error: {str(e)}", 500

@app.route('/admin/challans.json')
def admin_challans_json():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        challans = Challan.query.order_by(Challan.created_at.desc()).all()
        return jsonify({'data': [c.to_dict() for c in challans]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/admin/challans/new', methods=['GET', 'POST'])
def admin_challan_new():
    """Admin - Generate challan manually with full owner and vehicle details"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('admin/challan_new.html')
    # POST
    owner_name = (request.form.get('owner_name') or '').strip()
    vehicle_type = (request.form.get('vehicle_type') or '').strip()
    phone = (request.form.get('phone') or '').strip()
    registration_number = (request.form.get('registration_number') or '').strip().upper()
    challan_type = (request.form.get('challan_type') or '').strip()
    location = (request.form.get('location') or '').strip()
    amount_raw = (request.form.get('amount') or '').strip()
    if not all([owner_name, vehicle_type, registration_number, challan_type, location, amount_raw]):
        flash('All fields are required', 'danger')
        return render_template('admin/challan_new.html'), 400
    try:
        amount = float(amount_raw)
    except Exception:
        flash('Amount must be a number', 'danger')
        return render_template('admin/challan_new.html'), 400
    if not phone:
        phone = f'+91-98{random.randint(10000000,99999999)}'
    # Find or create owner
    owner = User.query.filter((User.phone == phone) | (User.username == owner_name)).first()
    if not owner:
        uname = owner_name.lower().replace(' ', '_')
        owner = User(
            username=uname,
            email=f'{uname}@example.com',
            phone=phone,
            password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
            user_type='owner',
            dl_number=f"UKDL-{random.randint(10,99)}-{random.randint(100000,999999)}"
        )
        db.session.add(owner)
        db.session.commit()
    # Find or create vehicle
    vehicle = Vehicle.query.filter_by(license_number=registration_number).first()
    if not vehicle:
        vehicle = Vehicle(
            license_number=registration_number,
            owner_id=owner.id,
            model='Unknown',
            vehicle_type=vehicle_type,
            registration_date=datetime.now(),
            insurance_expiry=datetime.now() + timedelta(days=365),
            state='Uttarakhand',
            city=location.split(',')[0] if location else 'Dehradun'
        )
        db.session.add(vehicle)
        db.session.commit()
    # Create challan
    challan = Challan(
        vehicle_id=vehicle.id,
        uin=f"UIN-{uuid.uuid4().hex[:12].upper()}",
        violation_type=challan_type,
        location=location,
        fine_amount=amount,
        status='Unpaid',
        due_date=datetime.now() + timedelta(days=30)
    )
    db.session.add(challan)
    db.session.commit()
    try:
        import csv, os
        csv_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(csv_dir, exist_ok=True)
        csv_path = os.path.join(csv_dir, 'challan_generation.csv')
        write_header = not os.path.exists(csv_path)
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(['timestamp','license_number','owner_name','vehicle_type','challan_type','location','amount','challan_id','uin'])
            writer.writerow([datetime.now().isoformat(), registration_number, owner_name, vehicle_type, challan_type, location, amount, challan.id, challan.uin])
    except Exception:
        pass
    try:
        if owner.phone:
            send_sms(owner.phone, f"Challan issued for {vehicle.license_number}. Violation: {challan_type}, Fine: ₹{amount}. UIN: {challan.uin}")
    except Exception:
        pass
    flash(f'Challan created: #{challan.id} for {vehicle.license_number}', 'success')
    return redirect(url_for('admin_challans'))

@app.route('/admin/challan/<int:challan_id>')
def admin_challan_detail(challan_id):
    """Admin detailed challan view."""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('login'))
    challan = Challan.query.get_or_404(challan_id)
    owner = challan.vehicle.owner if challan.vehicle else None
    return render_template('admin/challan_detail.html', challan=challan, owner=owner)

@app.route('/public/lookup', methods=['GET', 'POST'])
def public_lookup():
    """Public challan lookup by UIN / Vehicle No / DL No with optional city filter."""
    results = []
    q = request.values.get('q', '').strip()
    city = request.values.get('city', '').strip()
    if q:
        q_norm = q.strip()
        q_upper = q_norm.upper()

        # Use outerjoin to include challans even if owner has no DL number
        query = Challan.query.join(Vehicle).outerjoin(User, Vehicle.owner_id == User.id)

        # Support searching by:
        # - Exact / partial UIN
        # - Exact / partial Vehicle number
        # - Exact / partial DL number
        # - Numeric challan id (e.g., "12" or "#12")
        or_filters = []

        # numeric challan id
        q_digits = q_norm.replace('#', '').strip()
        if q_digits.isdigit():
            or_filters.append(Challan.id == int(q_digits))

        # use like for partial match (case-insensitive for SQLite compatibility)
        like = f"%{q_norm}%"
        like_upper = f"%{q_upper}%"
        
        # Search by UIN and Vehicle number (primary search)
        or_filters.extend([
            Challan.uin.like(like),
            Challan.uin.like(like_upper),
            Vehicle.license_number.like(like),
            Vehicle.license_number.like(like_upper),
        ])
        
        # Also search by DL number if user exists
        or_filters.extend([
            User.dl_number.like(like),
            User.dl_number.like(like_upper),
        ])

        query = query.filter(db.or_(*or_filters))
        if city:
            query = query.filter(Vehicle.city == city)
        results = query.order_by(Challan.created_at.desc()).limit(50).all()
    cities = [r[0] for r in db.session.query(Vehicle.city).distinct().filter(Vehicle.city.isnot(None)).all()]
    return render_template('public/lookup.html', q=q, city=city, cities=sorted(cities), results=results)

@app.route('/public/notices')
def public_notices():
    """Traffic notices (State/Central)."""
    from models import Notice
    notices = Notice.query.order_by(Notice.published_at.desc()).limit(50).all()
    return render_template('public/notices.html', notices=notices)

@app.route('/public/report', methods=['GET', 'POST'])
def public_report():
    """Report illegal activity / mishap."""
    from models import Report
    if request.method == 'POST':
        report_type = request.form.get('report_type')
        city = request.form.get('city')
        location = request.form.get('location')
        details = request.form.get('details')
        r = Report(
            reporter_user_id=session.get('user_id'),
            report_type=report_type,
            city=city,
            location=location,
            details=details
        )
        db.session.add(r)
        db.session.commit()

        # Email the report (configurable SMTP). Sends to karan2609n@gmail.com by default.
        try:
            from email_service import send_email
            import os as _os
            to_email = _os.environ.get("REPORT_TO_EMAIL", "karan2609n@gmail.com")
            subject = f"AutoFINE Incident Report - {report_type or 'report'} - {city or 'N/A'}"
            body = (
                f"New incident report submitted in AutoFINE.\n\n"
                f"Type: {report_type}\n"
                f"City: {city}\n"
                f"Location: {location}\n"
                f"Details:\n{details}\n\n"
                f"Reporter user id: {session.get('user_id')}\n"
            )
            send_email(to_email, subject, body)
        except Exception as e:
            # Do not block the report if email is not configured
            print(f"Report email not sent: {e}")

        flash('Report submitted successfully.', 'success')
        return redirect(url_for('public_report'))
    cities = [r[0] for r in db.session.query(Vehicle.city).distinct().filter(Vehicle.city.isnot(None)).all()]
    return render_template('public/report.html', cities=sorted(cities))

@app.route('/admin/challan/generate', methods=['POST'])
def admin_challan_generate():
    """Challan generation (manual entry, CSV logging)"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    owner_name = (request.form.get('owner_name') or '').strip()
    vehicle_type = (request.form.get('vehicle_type') or '').strip()
    challan_type = (request.form.get('challan_type') or '').strip()
    location = request.form.get('location', 'Unknown')
    manual_license_number = (request.form.get('license_number') or '').strip().upper()
    amount_raw = (request.form.get('amount') or '').strip()
    
    if not challan_type:
        return jsonify({'error': 'Challan type is required'}), 400
    if not manual_license_number:
        return jsonify({'error': 'Number plate is required. Please enter manually.'}), 400
    if not owner_name:
        return jsonify({'error': 'Owner name is required'}), 400
    if not vehicle_type:
        return jsonify({'error': 'Vehicle type is required'}), 400
    try:
        amount = float(amount_raw)
    except Exception:
        return jsonify({'error': 'Amount must be a number'}), 400
    
    try:
        from sqlalchemy import text
        license_number = manual_license_number
        vehicle = Vehicle.query.filter_by(license_number=license_number).first()
        if not vehicle:
            res = db.session.execute(text("SELECT id FROM users WHERE user_type='owner' ORDER BY id LIMIT 1")).first()
            owner_id = (res[0] if res else session.get('user_id'))
            if not owner_id:
                return jsonify({'error': 'Unauthorized'}), 401
            
            vehicle = Vehicle(
                license_number=license_number,
                owner_id=owner_id,
                model='Unknown',
                vehicle_type=vehicle_type,
                registration_date=datetime.now(),
                insurance_expiry=datetime.now() + timedelta(days=365),
                state='Uttarakhand',
                city=location.split(',')[0] if location else 'Dehradun'
            )
            db.session.add(vehicle)
            db.session.commit()
        
        fine_amount = amount if amount > 0 else calculate_fine(challan_type, vehicle.id)[0]
        _, is_subsequent, court_mandatory = calculate_fine(challan_type, vehicle.id)
        status = 'Court' if court_mandatory else 'Unpaid'
        license_action = "Suspend 3 months" if challan_type == "No Helmet" and is_subsequent else None
        
        challan = Challan(
            vehicle_id=vehicle.id,
            uin=f"UIN-{uuid.uuid4().hex[:12].upper()}",
            violation_type=challan_type,
            location=location,
            fine_amount=fine_amount,
            status=status,
            due_date=datetime.now() + timedelta(days=30),
        )
        db.session.add(challan)
        db.session.commit()
        
        # Append to CSV log
        try:
            import csv, os
            csv_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(csv_dir, exist_ok=True)
            csv_path = os.path.join(csv_dir, 'challan_generation.csv')
            write_header = not os.path.exists(csv_path)
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(['timestamp','license_number','owner_name','vehicle_type','challan_type','location','amount','challan_id','uin'])
                writer.writerow([
                    datetime.now().isoformat(),
                    license_number,
                    owner_name,
                    vehicle_type,
                    challan_type,
                    location,
                    fine_amount,
                    challan.id,
                    challan.uin
                ])
        except Exception:
            pass
        
        try:
            owner = vehicle.owner
            if owner and owner.phone:
                if status == "Court":
                    send_sms(owner.phone, f"Court Challan issued. UIN: {challan.uin}, Vehicle: {vehicle.license_number}, Violation: {challan_type}. Visit court for further process.")
                else:
                    send_sms(owner.phone, f"Challan issued. UIN: {challan.uin}, Vehicle: {vehicle.license_number}, Violation: {challan_type}, Fine: ₹{fine_amount}.")
        except Exception:
            pass
        
        return jsonify({
            'success': True,
            'license_number': license_number,
            'owner_name': owner_name,
            'challan_id': challan.id,
            'fine_amount': fine_amount,
            'uin': challan.uin,
            'status': challan.status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/process_violation', methods=['POST'])
def process_violation_compat():
    """Compatibility: accept old 'Process Violation' form and map to challan generation"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    owner_name = (request.form.get('owner_name') or 'Unknown').strip()
    vehicle_type = (request.form.get('vehicle_type') or 'Car').strip()
    challan_type = (request.form.get('challan_type') or request.form.get('violation_type') or '').strip()
    location = request.form.get('location', 'Unknown')
    manual_license_number = (request.form.get('license_number') or '').strip().upper()
    amount_raw = (request.form.get('amount') or '0').strip()
    if not challan_type:
        return jsonify({'error': 'Challan type is required'}), 400
    if not manual_license_number:
        return jsonify({'error': 'Number plate is required. Please enter manually.'}), 400
    try:
        amount = float(amount_raw)
    except Exception:
        amount = 0.0
    try:
        from sqlalchemy import text
        license_number = manual_license_number
        vehicle = Vehicle.query.filter_by(license_number=license_number).first()
        if not vehicle:
            res = db.session.execute(text("SELECT id FROM users WHERE user_type='owner' ORDER BY id LIMIT 1")).first()
            owner_id = (res[0] if res else session.get('user_id'))
            if not owner_id:
                return jsonify({'error': 'Unauthorized'}), 401
            vehicle = Vehicle(
                license_number=license_number,
                owner_id=owner_id,
                model='Unknown',
                vehicle_type=vehicle_type,
                registration_date=datetime.now(),
                insurance_expiry=datetime.now() + timedelta(days=365),
                state='Uttarakhand',
                city=location.split(',')[0] if location else 'Dehradun'
            )
            db.session.add(vehicle)
            db.session.commit()
        fine_amount = amount if amount > 0 else calculate_fine(challan_type, vehicle.id)[0]
        _, is_subsequent, court_mandatory = calculate_fine(challan_type, vehicle.id)
        status = 'Court' if court_mandatory else 'Unpaid'
        challan = Challan(
            vehicle_id=vehicle.id,
            uin=f"UIN-{uuid.uuid4().hex[:12].upper()}",
            violation_type=challan_type,
            location=location,
            fine_amount=fine_amount,
            status=status,
            due_date=datetime.now() + timedelta(days=30),
        )
        db.session.add(challan)
        db.session.commit()
        try:
            import csv, os
            csv_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(csv_dir, exist_ok=True)
            csv_path = os.path.join(csv_dir, 'challan_generation.csv')
            write_header = not os.path.exists(csv_path)
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(['timestamp','license_number','owner_name','vehicle_type','challan_type','location','amount','challan_id','uin'])
                writer.writerow([datetime.now().isoformat(), license_number, owner_name, vehicle_type, challan_type, location, fine_amount, challan.id, challan.uin])
        except Exception:
            pass
        return jsonify({
            'success': True,
            'license_number': license_number,
            'owner_name': owner_name,
            'challan_id': challan.id,
            'fine_amount': fine_amount,
            'uin': challan.uin,
            'status': challan.status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/challan/<int:challan_id>/pay', methods=['POST'])
def pay_challan(challan_id):
    """Mark challan as paid (payment gateway integration can be added later)"""
    challan = Challan.query.get_or_404(challan_id)
    
    if session.get('user_type') == 'admin':
        challan.status = 'Paid'
        challan.paid_at = datetime.now()
        db.session.commit()
        try:
            owner = challan.vehicle.owner if challan.vehicle else None
            phone = getattr(owner, "phone", None) if owner else None
            if phone:
                send_sms(phone, f"Challan #{challan.id} for {challan.vehicle.license_number if challan.vehicle else ''} has been paid. Amount: ₹{challan.fine_amount}.")
        except Exception:
            pass
        return jsonify({'success': True, 'message': 'Challan marked as paid'})
    
    return jsonify({'error': 'Unauthorized'}), 401

@app.route('/api/payments/mock', methods=['POST'])
def mock_payment():
    """Mock payment gateway for challans; marks paid and sends SMS."""
    data = request.get_json() or {}
    password = data.get('password')
    if password != '1234':
        return jsonify({'error': 'Payment password required'}), 403
    challan_id = data.get('challan_id')
    payment_ref = data.get('payment_ref', f"UKPAY-{int(time.time())}")
    if not challan_id:
        return jsonify({'error': 'challan_id required'}), 400
    challan = Challan.query.get_or_404(challan_id)
    if challan.status == 'Court' or challan.violation_type == 'Drunk Driving':
        return jsonify({'error': 'Court challan cannot be paid online', 'challan_id': challan.id}), 400
    if challan.status == 'Paid':
        return jsonify({'success': True, 'message': 'Already paid', 'payment_ref': payment_ref})
    challan.status = 'Paid'
    challan.paid_at = datetime.now()
    challan.notes = f"Mock payment ref: {payment_ref}"
    db.session.commit()
    try:
        owner = challan.vehicle.owner if challan.vehicle else None
        phone = getattr(owner, "phone", None) if owner else None
        if phone:
            send_sms(phone, f"Payment received for Challan #{challan.id} ({challan.violation_type}). Amount: ₹{challan.fine_amount}. Ref: {payment_ref}")
    except Exception:
        pass
    return jsonify({'success': True, 'payment_ref': payment_ref, 'challan_id': challan.id})


# ---------- Razorpay Payment Gateway ----------
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')

@app.route('/api/razorpay/create-order', methods=['POST'])
def razorpay_create_order():
    """Create a Razorpay order for challan payment. Returns order_id and key for checkout."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        return jsonify({
            'error': 'Razorpay not configured',
            'fallback_mock': True,
            'message': 'Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET. Using mock payment for now.'
        }), 503
    data = request.get_json() or {}
    if data.get('password') != '1234':
        return jsonify({'error': 'Payment password required'}), 403
    challan_id = data.get('challan_id')
    if not challan_id:
        return jsonify({'error': 'challan_id required'}), 400
    challan = Challan.query.get_or_404(challan_id)
    if challan.status == 'Paid':
        return jsonify({'error': 'Challan already paid'}), 400
    if challan.status == 'Court' or challan.violation_type == 'Drunk Driving':
        return jsonify({'error': 'Court challan cannot be paid online'}), 400
    # Verify owner
    if session.get('user_type') == 'owner':
        vehicles = Vehicle.query.filter_by(owner_id=session['user_id']).all()
        vehicle_ids = [v.id for v in vehicles]
        if challan.vehicle_id not in vehicle_ids:
            return jsonify({'error': 'Not your challan'}), 403
    amount_paise = int(round(challan.fine_amount * 100))
    if amount_paise < 100:
        amount_paise = 100
    try:
        try:
            import razorpay
        except ImportError:
            return jsonify({
                'error': 'Razorpay package not installed. Run: pip install razorpay',
                'fallback_mock': True
            }), 503
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        order_data = {
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': f'challan_{challan.id}_{uuid.uuid4().hex[:8]}',
            'notes': {'challan_id': str(challan.id), 'uin': challan.uin or ''}
        }
        order = client.order.create(data=order_data)
        return jsonify({
            'success': True,
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key_id': RAZORPAY_KEY_ID,
            'challan_id': challan_id,
            'uin': challan.uin
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/razorpay/verify', methods=['POST'])
def razorpay_verify():
    """Verify Razorpay payment signature and mark challan as paid."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    if not RAZORPAY_KEY_SECRET:
        return jsonify({'error': 'Razorpay not configured'}), 503
    data = request.get_json() or {}
    if data.get('password') != '1234':
        return jsonify({'error': 'Payment password required'}), 403
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')
    challan_id = data.get('challan_id')
    if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature, challan_id]):
        return jsonify({'error': 'Missing payment details'}), 400
    challan = Challan.query.get_or_404(challan_id)
    if challan.status == 'Paid':
        return jsonify({'success': True, 'message': 'Already paid', 'challan_id': challan.id})
    try:
        try:
            import razorpay
        except ImportError:
            return jsonify({'error': 'Razorpay package not installed'}), 503
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        client.utility.verify_payment_signature(params_dict)
        challan.status = 'Paid'
        challan.paid_at = datetime.now()
        challan.payment_ref = razorpay_payment_id
        challan.notes = (challan.notes or '') + f' Razorpay: {razorpay_payment_id}'
        db.session.commit()
        try:
            owner = challan.vehicle.owner if challan.vehicle else None
            phone = getattr(owner, 'phone', None) if owner else None
            if phone:
                send_sms(phone, f"Payment received for Challan #{challan.id}. Amount: ₹{challan.fine_amount}. Ref: {razorpay_payment_id}")
        except Exception:
            pass
        return jsonify({
            'success': True,
            'message': 'Payment successful',
            'challan_id': challan.id,
            'payment_id': razorpay_payment_id
        })
    except Exception as e:
        err_msg = str(e).lower()
        if 'signature' in err_msg or 'verification' in err_msg:
            return jsonify({'error': 'Invalid payment signature'}), 400
        return jsonify({'error': str(e)}), 500


@app.route('/api/realtime/challans')
def realtime_challans():
    """Server-Sent Events endpoint for real-time challan updates"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    def generate():
        user_id = session['user_id']
        user_type = session.get('user_type', 'owner')
        
        # Get initial state
        if user_type == 'owner':
            vehicles = Vehicle.query.filter_by(owner_id=user_id).all()
            vehicle_ids = [v.id for v in vehicles]
            last_count = Challan.query.filter(Challan.vehicle_id.in_(vehicle_ids)).count()
        else:
            last_count = Challan.query.count()
        
        yield f"data: {json.dumps({'type': 'init', 'count': last_count})}\n\n"
        
        while True:
            try:
                # Check for new challans every 2 seconds
                time.sleep(2)
                
                if user_type == 'owner':
                    vehicles = Vehicle.query.filter_by(owner_id=user_id).all()
                    vehicle_ids = [v.id for v in vehicles]
                    current_count = Challan.query.filter(Challan.vehicle_id.in_(vehicle_ids)).count()
                    recent_challans = Challan.query.filter(
                        Challan.vehicle_id.in_(vehicle_ids)
                    ).order_by(Challan.created_at.desc()).limit(5).all()
                else:
                    current_count = Challan.query.count()
                    recent_challans = Challan.query.order_by(Challan.created_at.desc()).limit(5).all()
                
                if current_count != last_count:
                    challan_data = [{
                        'id': c.id,
                        'license_number': c.vehicle.license_number if c.vehicle else 'N/A',
                        'violation_type': c.violation_type,
                        'fine_amount': c.fine_amount,
                        'status': c.status,
                        'created_at': c.created_at.isoformat()
                    } for c in recent_challans]
                    
                    yield f"data: {json.dumps({'type': 'update', 'count': current_count, 'challans': challan_data})}\n\n"
                    last_count = current_count
                
                # Send heartbeat
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                break
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/api/realtime/vehicle/<int:vehicle_id>/challans')
def realtime_vehicle_challans(vehicle_id):
    """Real-time updates for specific vehicle's challans"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.owner_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    def generate():
        last_count = Challan.query.filter_by(vehicle_id=vehicle_id).count()
        yield f"data: {json.dumps({'type': 'init', 'count': last_count})}\n\n"
        
        while True:
            try:
                time.sleep(3)
                current_count = Challan.query.filter_by(vehicle_id=vehicle_id).count()
                
                if current_count != last_count:
                    challans = Challan.query.filter_by(vehicle_id=vehicle_id).order_by(Challan.created_at.desc()).all()
                    challan_data = [{
                        'id': c.id,
                        'violation_type': c.violation_type,
                        'location': c.location,
                        'fine_amount': c.fine_amount,
                        'status': c.status,
                        'due_date': c.due_date.isoformat() if c.due_date else None,
                        'created_at': c.created_at.isoformat()
                    } for c in challans]
                    
                    yield f"data: {json.dumps({'type': 'update', 'count': current_count, 'challans': challan_data})}\n\n"
                    last_count = current_count
                
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                break
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

# ==================== GEMINI-POWERED FEATURES ====================

@app.route('/api/gemini/news')
def gemini_news():
    """Get real-time traffic news from Gemini"""
    try:
        news = generate_traffic_news()
        return jsonify(news)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gemini/rules/<violation_type>')
def gemini_rules(violation_type):
    """Get traffic rules explanation from Gemini"""
    try:
        explanation = get_traffic_rules_explanation(violation_type)
        return jsonify({'violation_type': violation_type, 'explanation': explanation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gemini/insights')
def gemini_insights():
    """Get predictive traffic insights from Gemini"""
    location = request.args.get('location')
    try:
        insights = get_predictive_insights(location)
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gemini/appeal-guidance', methods=['POST'])
def gemini_appeal_guidance():
    """Get AI guidance for appealing a challan"""
    data = request.get_json()
    challan_id = data.get('challan_id')
    
    if not challan_id:
        return jsonify({'error': 'challan_id required'}), 400
    
    challan = Challan.query.get_or_404(challan_id)
    challan_details = challan.to_dict()
    
    try:
        guidance = generate_appeal_guidance(challan_details)
        return jsonify({'guidance': guidance, 'challan_id': challan_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== POINT SYSTEM ====================

@app.route('/api/driver-license/<dl_number>/points')
def get_driver_points(dl_number):
    """Get driver license points"""
    license = DriverLicense.query.filter_by(dl_number=dl_number).first()
    if not license:
        return jsonify({'error': 'License not found'}), 404
    
    return jsonify({
        'dl_number': license.dl_number,
        'points': license.points,
        'status': license.status,
        'expiry_date': license.expiry_date.isoformat() if license.expiry_date else None
    })

@app.route('/api/challan/<int:challan_id>/deduct-points', methods=['POST'])
def deduct_points(challan_id):
    """Deduct points from driver license after challan"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    challan = Challan.query.get_or_404(challan_id)
    user = challan.vehicle.owner if challan.vehicle else None
    
    if not user or not user.dl_number:
        return jsonify({'error': 'Driver license not found'}), 404
    
    license = DriverLicense.query.filter_by(dl_number=user.dl_number).first()
    if not license:
        # Create license if doesn't exist
        license = DriverLicense(
            dl_number=user.dl_number,
            user_id=user.id,
            points=12
        )
        db.session.add(license)
    
    # Deduct points based on violation severity
    points_deducted = 2 if challan.violation_type in ['Drunk Driving', 'Speeding'] else 1
    
    license.points = max(0, license.points - points_deducted)
    
    # Suspend if points <= 0
    if license.points <= 0:
        license.status = 'Suspended'
        send_sms(user.phone, f"Your license {license.dl_number} has been suspended due to point deduction.")
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'points_deducted': points_deducted,
        'remaining_points': license.points,
        'status': license.status
    })

# ==================== VIRTUAL COURT / APPEALS ====================

@app.route('/api/appeals', methods=['POST'])
def create_appeal():
    """Create an appeal for a challan"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    challan_id = data.get('challan_id')
    reason = data.get('reason')
    
    if not challan_id or not reason:
        return jsonify({'error': 'challan_id and reason required'}), 400
    
    challan = Challan.query.get_or_404(challan_id)
    
    # Verify ownership
    if challan.vehicle.owner_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    appeal = Appeal(
        challan_id=challan_id,
        user_id=session['user_id'],
        reason=reason,
        status='Pending'
    )
    db.session.add(appeal)
    challan.status = 'Disputed'
    db.session.commit()
    
    # Get AI guidance
    try:
        guidance = generate_appeal_guidance(challan.to_dict())
    except:
        guidance = "Your appeal has been submitted. It will be reviewed by authorities."
    
    return jsonify({
        'success': True,
        'appeal_id': appeal.id,
        'guidance': guidance
    })

@app.route('/api/appeals/<int:appeal_id>/review', methods=['POST'])
def review_appeal(appeal_id):
    """Review an appeal (admin only)"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    status = data.get('status')  # Approved or Rejected
    notes = data.get('notes', '')
    
    appeal = Appeal.query.get_or_404(appeal_id)
    appeal.status = status
    appeal.reviewed_at = datetime.now()
    appeal.reviewer_notes = notes
    
    if status == 'Approved':
        appeal.challan.status = 'Paid'
        appeal.challan.notes = 'Appeal approved - challan waived'
    else:
        appeal.challan.status = 'Unpaid'
    
    db.session.commit()
    
    return jsonify({'success': True, 'status': status})

# ==================== PAYMENT PLANS ====================

@app.route('/api/payment-plans', methods=['POST'])
def create_payment_plan():
    """Create installment payment plan"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    challan_id = data.get('challan_id')
    installment_count = data.get('installment_count', 3)
    
    if not challan_id:
        return jsonify({'error': 'challan_id required'}), 400
    
    challan = Challan.query.get_or_404(challan_id)
    
    if challan.fine_amount < 5000:
        return jsonify({'error': 'Payment plans available only for fines above ₹5000'}), 400
    
    if PaymentPlan.query.filter_by(challan_id=challan_id).first():
        return jsonify({'error': 'Payment plan already exists'}), 400
    
    installment_amount = challan.fine_amount / installment_count
    
    plan = PaymentPlan(
        challan_id=challan_id,
        total_amount=challan.fine_amount,
        remaining_amount=challan.fine_amount,
        installment_count=installment_count,
        current_installment=0,
        next_due_date=datetime.now().date() + timedelta(days=30),
        status='Active'
    )
    db.session.add(plan)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'plan_id': plan.id,
        'installment_amount': installment_amount,
        'next_due_date': plan.next_due_date.isoformat()
    })

@app.route('/api/payment-plans/<int:plan_id>/pay-installment', methods=['POST'])
def pay_installment(plan_id):
    """Pay an installment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    plan = PaymentPlan.query.get_or_404(plan_id)
    
    if plan.status != 'Active':
        return jsonify({'error': 'Payment plan not active'}), 400
    
    installment_amount = plan.total_amount / plan.installment_count
    plan.remaining_amount -= installment_amount
    plan.current_installment += 1
    
    if plan.remaining_amount <= 0:
        plan.status = 'Completed'
        plan.challan.status = 'Paid'
        plan.challan.paid_at = datetime.now()
    else:
        plan.next_due_date = datetime.now().date() + timedelta(days=30)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'remaining_amount': plan.remaining_amount,
        'status': plan.status
    })

# ==================== ANALYTICS & PREDICTIVE INSIGHTS ====================

@app.route('/api/analytics/dashboard')
def analytics_dashboard():
    """Get analytics data for dashboard"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get violation statistics
    violations = db.session.query(
        Challan.violation_type,
        db.func.count(Challan.id).label('count')
    ).group_by(Challan.violation_type).all()
    
    # Get location hotspots
    hotspots = db.session.query(
        Challan.location,
        db.func.count(Challan.id).label('count')
    ).filter(Challan.location.isnot(None)).group_by(Challan.location).order_by(db.func.count(Challan.id).desc()).limit(10).all()
    
    # Get time-based patterns
    hourly_violations = db.session.query(
        db.func.strftime('%H', Challan.created_at).label('hour'),
        db.func.count(Challan.id).label('count')
    ).group_by('hour').all()
    
    # Get Gemini insights
    try:
        gemini_insights = get_predictive_insights()
    except:
        gemini_insights = {}
    
    return jsonify({
        'violations': [{'type': v[0], 'count': v[1]} for v in violations],
        'hotspots': [{'location': h[0], 'count': h[1]} for h in hotspots],
        'hourly_patterns': [{'hour': int(h[0]), 'count': h[1]} for h in hourly_violations],
        'predictive_insights': gemini_insights
    })

# ==================== AI CHATBOT FOR GRIEVANCES ====================

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """AI chatbot for grievances and queries"""
    data = request.get_json()
    message = data.get('message', '')
    context = data.get('context', {})
    
    if not message:
        return jsonify({'error': 'message required'}), 400
    
    model = get_gemini_model()
    if not model:
        return jsonify({'response': 'Chatbot service temporarily unavailable. Please contact support.'})
    
    try:
        prompt = (
            "Your name is Bob. You are friendly, frank, and helpful. Keep answers simple and approachable. "
            "Answer any question. If the query is about Indian transportation (traffic rules, challans, RTO, RC/DL, road safety), "
            "add authoritative details (rule purpose, common violations, penalties) and step-by-step portal guidance where relevant. "
            "Do not encourage unlawful behavior.\n\n"
            f"User: {message}\n\n"
            f"Context: {json.dumps(context)}\n\n"
            "Provide a concise, professional response that users can easily understand."
        )
        response = model.generate_content(prompt)
        text = (response.text or '').strip()
        if not text:
            text = "I’m here to help. Please tell me what you’d like to know."
        if "Bob" not in text:
            text = f"{text}\n— Bob"
        return jsonify({'response': text})
    except Exception as e:
        return jsonify({'response': f'I apologize, but I encountered an error. Please try rephrasing your question. Error: {str(e)}'})

# ==================== GEMINI NOTICES ====================

@app.route('/api/gemini/notices')
def gemini_notices():
    """Generate fresh traffic notices/rules updates using Gemini (AI-generated)."""
    try:
        model = get_gemini_model()
        if not model:
            return jsonify({'success': False, 'error': 'Gemini not available'}), 503

        prompt = f"""Generate 6 concise traffic notices for India (mix Central + State, include Uttarakhand). 
Each notice should be realistic and citizen-friendly.

Return STRICT JSON array. Each item fields:
- scope: Central or State
- title
- body (2-3 lines)
- state (null for Central)
- city (null or a city)

Date: {datetime.now().strftime('%Y-%m-%d')}
"""
        resp = model.generate_content(prompt)
        text = (resp.text or '').strip()

        # Extract JSON array from response
        if '[' in text and ']' in text:
            start = text.find('[')
            end = text.rfind(']') + 1
            arr = json.loads(text[start:end])
        else:
            arr = []

        # Normalize
        out = []
        for item in arr[:10]:
            out.append({
                'scope': item.get('scope') or 'Central',
                'title': item.get('title') or 'Traffic Notice',
                'body': item.get('body') or '',
                'state': item.get('state'),
                'city': item.get('city'),
                'published_at': datetime.now().strftime('%Y-%m-%d')
            })

        return jsonify({'success': True, 'notices': out})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== ADVANCED DETECTION SERVICES ====================

@app.route('/api/detection/anpr', methods=['POST'])
def anpr_detection():
    """ANPR detection endpoint"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400
    
    file = request.files['image']
    camera_id = request.form.get('camera_id')
    
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp}_{filename}'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        result = ANPRService.detect_from_image(filepath, camera_id)
        
        # Check for stolen vehicle
        if result['license_number']:
            stolen_check = StolenVehicleService.check_vehicle_status(result['license_number'])
            if stolen_check.get('is_stolen'):
                result['stolen_alert'] = stolen_check
                # Notify police
                StolenVehicleService.notify_police_units(
                    result['license_number'],
                    result.get('gps_coords', {}),
                    'unknown'
                )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detection/speed', methods=['POST'])
def speed_detection():
    """Speed detection endpoint"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    license_number = data.get('license_number')
    speed_limit = data.get('speed_limit', 60)  # Default 60 km/h
    actual_speed = data.get('actual_speed')
    location = data.get('location', 'Unknown')
    
    if not license_number or not actual_speed:
        return jsonify({'error': 'license_number and actual_speed required'}), 400
    
    try:
        violation = SpeedDetectionService.detect_speeding(
            license_number, speed_limit, actual_speed, location
        )
        
        if violation:
            return jsonify({'violation': violation})
        else:
            return jsonify({'message': 'No violation detected', 'speed': actual_speed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detection/stolen-check/<license_number>')
def check_stolen(license_number):
    """Check if vehicle is stolen"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        status = StolenVehicleService.check_vehicle_status(license_number)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detection/predictive-hotspots')
def predictive_hotspots():
    """Get predictive violation hotspots"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get historical data (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        historical_challans = Challan.query.filter(
            Challan.created_at >= seven_days_ago
        ).all()
        
        hotspots = PredictivePolicingService.predict_violation_hotspots(
            historical_challans, '7d'
        )
        
        return jsonify({'hotspots': hotspots})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictive/city')
def predictive_city_insights():
    """City-specific AI traffic insights (Gemini-based)."""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    city = (request.args.get('city') or '').strip()
    if not city:
        return jsonify({'success': False, 'error': 'city is required'}), 400

    # Basic city -> lat/lon (demo defaults)
    city_coords = {
        'dehradun': {'city': 'Dehradun', 'lat': 30.3165, 'lon': 78.0322},
        'haldwani': {'city': 'Haldwani', 'lat': 29.2183, 'lon': 79.5130},
        'almora': {'city': 'Almora', 'lat': 29.5971, 'lon': 79.6591},
        'khatima': {'city': 'Khatima', 'lat': 28.9216, 'lon': 79.9709},
        'delhi': {'city': 'Delhi', 'lat': 28.6139, 'lon': 77.2090},
        'mumbai': {'city': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
        'bengaluru': {'city': 'Bengaluru', 'lat': 12.9716, 'lon': 77.5946},
        'kolkata': {'city': 'Kolkata', 'lat': 22.5726, 'lon': 88.3639},
        'chennai': {'city': 'Chennai', 'lat': 13.0827, 'lon': 80.2707},
        'hyderabad': {'city': 'Hyderabad', 'lat': 17.3850, 'lon': 78.4867},
        'pune': {'city': 'Pune', 'lat': 18.5204, 'lon': 73.8567},
        'lucknow': {'city': 'Lucknow', 'lat': 26.8467, 'lon': 80.9462},
    }
    key = city.lower().strip()
    city_info = city_coords.get(key, {'city': city, 'lat': None, 'lon': None})

    # Use existing hotspot analytics as "live" context (from our DB)
    hotspots = db.session.query(
        Challan.location,
        db.func.count(Challan.id).label('count')
    ).filter(Challan.location.isnot(None)).group_by(Challan.location).order_by(db.func.count(Challan.id).desc()).limit(5).all()

    try:
        insights = get_predictive_insights(location=city)
    except Exception:
        insights = {
            "hotspot": "High traffic areas",
            "peak_time": "Rush hours",
            "common_violation": "Traffic violations",
            "recommendation": "Drive safely and follow rules"
        }

    # Note: This is AI-generated; true real-time traffic needs a live traffic provider API.
    return jsonify({
        'success': True,
        'city': city_info['city'],
        'city_info': city_info,
        'insights': insights,
        'hotspots': [{'location': h[0], 'count': h[1]} for h in hotspots]
    })

@app.route('/api/detection/patrol-routes')
def patrol_routes():
    """Get suggested patrol routes"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    available_units = request.args.get('available_units', 5, type=int)
    
    try:
        # Get hotspots first
        from datetime import timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        historical_challans = Challan.query.filter(
            Challan.created_at >= seven_days_ago
        ).all()
        
        hotspots = PredictivePolicingService.predict_violation_hotspots(
            historical_challans, '7d'
        )
        
        routes = PredictivePolicingService.suggest_patrol_routes(hotspots, available_units)
        
        return jsonify({'routes': routes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== BHOPAL ITMS INTEGRATION ====================

@app.route('/api/bhopal-itms/no-helmet', methods=['POST'])
def bhopal_no_helmet_detection():
    """Bhopal ITMS No Helmet Detection - First in India"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400
    
    file = request.files['image']
    license_number = request.form.get('license_number')
    
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp}_{filename}'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Detect helmet violations
        result = BhopalITMSService.detect_no_helmet_violation(filepath, license_number)
        
        # If violations detected, create challans
        challans_created = []
        if result['violations']:
            vehicle = Vehicle.query.filter_by(license_number=license_number).first()
            if not vehicle:
                return jsonify({'error': 'Vehicle not found. Please register vehicle first.'}), 404
            
            for violation in result['violations']:
                fine_amount, is_subsequent, court_mandatory = calculate_fine(violation['violation_type'], vehicle.id)
                status = 'Court' if court_mandatory else 'Unpaid'
                license_action = "Suspend 3 months" if violation['violation_type'] == "No Helmet" and is_subsequent else None
                
                challan = Challan(
                    vehicle_id=vehicle.id,
                    uin=f"UIN-{uuid.uuid4().hex[:12].upper()}",
                    violation_type=violation['violation_type'],
                    location=request.form.get('location', 'Unknown'),
                    fine_amount=fine_amount,
                    evidence_image=filename,
                    status=status,
                    due_date=datetime.now() + timedelta(days=30),
                    is_subsequent=is_subsequent,
                    license_action=license_action
                )
                db.session.add(challan)
                challans_created.append(challan.id)
            
            db.session.commit()
            
            # Auto email challan
            for challan_id in challans_created:
                BhopalITMSService.auto_email_challan(challan_id)
        
        return jsonify({
            'success': True,
            'violations_detected': result['total_detected'],
            'violations': result['violations'],
            'challans_created': challans_created,
            'vehicle_type': result.get('vehicle_type')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bhopal-itms/classify-detect', methods=['POST'])
def bhopal_classify_and_detect():
    """Classify vehicle and detect all violations (Bhopal ITMS)"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400
    
    file = request.files['image']
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp}_{filename}'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        result = BhopalITMSService.classify_and_detect(filepath)
        
        # Also check for license plate
        anpr_result = ANPRService.detect_from_image(filepath)
        if anpr_result.get('license_number'):
            result['license_number'] = anpr_result['license_number']
            result['anpr_confidence'] = anpr_result.get('confidence')
            
            # Check if suspected vehicle
            suspected = BhopalITMSService.check_suspected_vehicle(anpr_result['license_number'])
            if suspected.get('is_suspected'):
                result['suspected_vehicle_alert'] = suspected
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bhopal-itms/suspected-vehicle/<license_number>')
def check_suspected_vehicle(license_number):
    """Check suspected vehicle (Bhopal ITMS)"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        result = BhopalITMSService.check_suspected_vehicle(license_number)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bhopal-itms/statistics')
def bhopal_statistics():
    """Get Bhopal ITMS style statistics"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    time_period = request.args.get('period', '24h')
    
    try:
        stats = BhopalITMSService.generate_statistics(time_period)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bhopal-itms/rto-integration/<license_number>')
def rto_integration(license_number):
    """RTO database integration (Bhopal ITMS)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        result = BhopalITMSService.integrate_with_rto(license_number)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== DATASET IMPORT ====================

@app.route('/api/datasets/import', methods=['POST'])
def import_datasets():
    """Import all available datasets from CSV files"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from dataset_importer import DatasetImporter
        importer = DatasetImporter(app)
        total_imported = importer.import_all_datasets()
        
        return jsonify({
            'success': True,
            'message': f'Successfully imported {total_imported} records from all datasets',
            'total_imported': total_imported
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/datasets/list')
def list_datasets():
    """List all available datasets"""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    import os
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    datasets = []

    def add_dataset(rel_path, name, dtype, source=None, rows=None):
        abs_path = os.path.join(base_path, *rel_path.split('/'))
        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            datasets.append({
                'id': rel_path.replace('\\', '/'),
                'name': name,
                'type': dtype,
                'size': os.path.getsize(abs_path),
                'rows': rows,
                'source': source or ''
            })
    
    # Check for Punjab dataset
    add_dataset('archive/Punjab_E_Challan_Dataset_500_Rows.csv', 'Punjab E-Challan Dataset', 'Individual Challan Records', source='archive/', rows=500)
    
    # Check for state statistics
    add_dataset('dataset/RS_Session_259_AU_1689_A.csv', 'State/District Statistics', 'State-wise Challan Statistics', source='dataset/')
    
    # Check for offence statistics
    add_dataset('dataset/RS_Session_267_AU_2175_A_and_C.csv', 'Offence Statistics', 'Offence-wise Statistics', source='dataset/')
    
    # Check for yearly statistics
    add_dataset('dataset/RS_Session_256_AU_93_D.csv', 'Yearly Statistics', 'Year-wise Challan Count', source='dataset/')
    
    # Check for revenue statistics
    add_dataset('dataset/RS_Session_266_AU_1849_E_i.csv', 'State Revenue Statistics', 'State-wise Revenue', source='dataset/')

    # data/ folder datasets
    add_dataset('data/Indian_Traffic_Violations.csv', 'Indian Traffic Violations', 'Violation Records (Synthetic/Compiled)', source='data/')
    add_dataset('data/traffic.csv', 'Traffic Flow Dataset', 'Traffic volume time-series', source='data/')
    add_dataset('data/police.csv', 'Police Stops Dataset', 'Police stop / enforcement records', source='data/')

    # Uploaded datasets (AutoFINE/uploads/datasets/*.csv)
    uploads_dir = os.path.join(base_path, 'AutoFINE', 'uploads', 'datasets')
    if os.path.exists(uploads_dir):
        for fn in os.listdir(uploads_dir):
            if fn.lower().endswith('.csv'):
                add_dataset(f'AutoFINE/uploads/datasets/{fn}', fn, 'Uploaded CSV', source='uploads/')
    
    return jsonify({
        'success': True,
        'datasets': datasets,
        'total': len(datasets)
    })

@app.route('/api/datasets/upload', methods=['POST'])
def upload_dataset():
    """Upload a CSV dataset from PC (admin only)."""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    f = request.files['file']
    if not f.filename or not f.filename.lower().endswith('.csv'):
        return jsonify({'success': False, 'error': 'Please upload a .csv file'}), 400

    import os
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(base_path, 'AutoFINE', 'uploads', 'datasets')
    os.makedirs(upload_dir, exist_ok=True)
    safe_name = secure_filename(f.filename)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_name = f"{stamp}_{safe_name}"
    out_path = os.path.join(upload_dir, out_name)
    f.save(out_path)

    return jsonify({'success': True, 'name': out_name, 'dataset_id': f"AutoFINE/uploads/datasets/{out_name}"})

def _detect_dataset_type(csv_abs_path: str) -> str:
    """Detect dataset type from header."""
    try:
        with open(csv_abs_path, 'r', encoding='utf-8', errors='ignore') as fh:
            header = fh.readline().strip().lower()
    except Exception:
        return 'unknown'

    if 'violation_id' in header and 'violation_type' in header and 'fine_amount' in header:
        return 'indian_violations'
    if 'datetime' in header and 'junction' in header and 'vehicles' in header:
        return 'traffic_flow'
    if 'stop_date' in header and 'stop_time' in header and 'violation' in header:
        return 'police_stops'
    if 'challan_id' in header and 'violation_type' in header and 'vehicle_type' in header:
        return 'punjab_challans'
    return 'unknown'

@app.route('/api/datasets/import-one', methods=['POST'])
def import_one_dataset():
    """Import one selected dataset by dataset_id (admin only)."""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    payload = request.get_json(silent=True) or {}
    dataset_id = (payload.get('dataset_id') or '').strip()
    if not dataset_id:
        return jsonify({'success': False, 'error': 'dataset_id is required'}), 400

    import os
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_path = os.path.join(base_path, *dataset_id.split('/'))
    if not os.path.exists(abs_path):
        return jsonify({'success': False, 'error': 'Dataset not found on server'}), 404

    from dataset_importer import DatasetImporter
    importer = DatasetImporter(app)
    dtype = _detect_dataset_type(abs_path)

    try:
        if dtype == 'indian_violations':
            n = importer.import_indian_traffic_violations(abs_path)
            return jsonify({'success': True, 'message': f'Imported {n} violation rows.'})
        if dtype == 'traffic_flow':
            n = importer.import_traffic_flow_data(abs_path)
            return jsonify({'success': True, 'message': f'Processed {n} junction records.'})
        if dtype == 'police_stops':
            n = importer.import_police_stop_data(abs_path)
            return jsonify({'success': True, 'message': f'Processed {n} violation types.'})
        if dtype == 'punjab_challans':
            n = importer.import_punjab_challan_dataset(abs_path)
            return jsonify({'success': True, 'message': f'Imported {n} challans.'})
        return jsonify({'success': False, 'error': 'Unsupported CSV format (could not detect dataset type).'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/datasets/import-url', methods=['POST'])
def import_dataset_from_url():
    """Download CSV from a URL, save, and import (admin only)."""
    if 'user_id' not in session or session.get('user_type') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    payload = request.get_json(silent=True) or {}
    url = (payload.get('url') or '').strip()
    if not url.lower().startswith(('http://', 'https://')):
        return jsonify({'success': False, 'error': 'Valid http(s) URL is required'}), 400

    import os
    import urllib.request
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(base_path, 'AutoFINE', 'uploads', 'datasets')
    os.makedirs(upload_dir, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_name = f"{stamp}_download.csv"
    out_path = os.path.join(upload_dir, out_name)

    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            data_bytes = resp.read()
        with open(out_path, 'wb') as fh:
            fh.write(data_bytes)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to download: {str(e)}'}), 400

    # Import it
    try:
        from dataset_importer import DatasetImporter
        importer = DatasetImporter(app)
        dtype = _detect_dataset_type(out_path)
        if dtype == 'indian_violations':
            n = importer.import_indian_traffic_violations(out_path)
            msg = f'Imported {n} violation rows from URL.'
        elif dtype == 'traffic_flow':
            n = importer.import_traffic_flow_data(out_path)
            msg = f'Processed {n} junction records from URL.'
        elif dtype == 'police_stops':
            n = importer.import_police_stop_data(out_path)
            msg = f'Processed {n} violation types from URL.'
        elif dtype == 'punjab_challans':
            n = importer.import_punjab_challan_dataset(out_path)
            msg = f'Imported {n} challans from URL.'
        else:
            return jsonify({'success': False, 'error': 'Unsupported CSV format (could not detect dataset type).'}), 400

        return jsonify({'success': True, 'message': msg})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Initialize default admin user
        if not User.query.filter_by(username='admin').first():
            admin_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(
                username='admin',
                email='admin@autofine.com',
                password_hash=admin_password,
                user_type='admin'
            )
            db.session.add(admin)
        
        # Initialize default violations
        violations = [
            {'type': 'Speeding', 'fine': 1000},
            {'type': 'Signal Jumping', 'fine': 500},
            {'type': 'Wrong Parking', 'fine': 1500},
            {'type': 'No Helmet', 'fine': 500},
            {'type': 'Red Light Violation', 'fine': 1000},
            {'type': 'Wrong Lane', 'fine': 750},
            {'type': 'Overloading', 'fine': 2000}
        ]
        
        for v in violations:
            if not Violation.query.filter_by(violation_type=v['type']).first():
                violation = Violation(
                    violation_type=v['type'],
                    fine_amount=v['fine']
                )
                db.session.add(violation)
        
        db.session.commit()
    
    # Get port from environment variable (Heroku sets this), default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Only enable debug in development, not production
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
