"""
Database Models for AutoFINE System
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create db instance - will be initialized by app.py
db = SQLAlchemy()

class User(db.Model):
    """User model (vehicle owners and admins)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    dl_number = db.Column(db.String(30), unique=True, index=True)  # Driving License number
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, default='owner')  # 'owner' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Vehicle(db.Model):
    """Vehicle model"""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    license_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    model = db.Column(db.String(100))
    color = db.Column(db.String(50))
    registration_date = db.Column(db.Date)
    insurance_expiry = db.Column(db.Date)
    vehicle_type = db.Column(db.String(50))  # Car, Bike, Truck, Bus
    state = db.Column(db.String(50), default="Uttarakhand")
    city = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    challans = db.relationship('Challan', backref='vehicle', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Vehicle {self.license_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'license_number': self.license_number,
            'model': self.model,
            'color': self.color,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'insurance_expiry': self.insurance_expiry.isoformat() if self.insurance_expiry else None,
            'vehicle_type': self.vehicle_type
        }

class Camera(db.Model):
    """Camera model for traffic cameras"""
    __tablename__ = 'cameras'
    
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    challans = db.relationship('Challan', backref='camera', lazy=True)
    
    def __repr__(self):
        return f'<Camera {self.camera_id} - {self.location}>'

class Violation(db.Model):
    """Violation types and their fine amounts"""
    __tablename__ = 'violations'
    
    id = db.Column(db.Integer, primary_key=True)
    violation_type = db.Column(db.String(100), unique=True, nullable=False)
    fine_amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Violation {self.violation_type}>'

class Challan(db.Model):
    """Challan/Ticket model"""
    __tablename__ = 'challans'
    
    id = db.Column(db.Integer, primary_key=True)
    uin = db.Column(db.String(40), unique=True, index=True)  # Unique Identification Number
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False, index=True)
    violation_type = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    fine_amount = db.Column(db.Float, nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey('cameras.id'))
    evidence_image = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Unpaid')  # 'Unpaid', 'Paid', 'Disputed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    due_date = db.Column(db.Date)
    paid_at = db.Column(db.DateTime)
    payment_ref = db.Column(db.String(60))
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Challan {self.id} - {self.vehicle.license_number if self.vehicle else "N/A"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'uin': self.uin,
            'vehicle_id': self.vehicle_id,
            'license_number': self.vehicle.license_number if self.vehicle else 'N/A',
            'violation_type': self.violation_type,
            'location': self.location,
            'fine_amount': self.fine_amount,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'payment_ref': self.payment_ref
        }
    
    def is_overdue(self):
        if self.status == 'Paid':
            return False
        if self.due_date:
            return datetime.now().date() > self.due_date
        return False


class Notice(db.Model):
    __tablename__ = 'notices'

    id = db.Column(db.Integer, primary_key=True)
    scope = db.Column(db.String(20), nullable=False, default="State")  # State/Central
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(50))
    city = db.Column(db.String(80))
    published_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reporter_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    report_type = db.Column(db.String(40), nullable=False)  # illegal_activity / mishap
    city = db.Column(db.String(80))
    location = db.Column(db.String(200))
    details = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class DriverLicense(db.Model):
    """Driver License with Point System"""
    __tablename__ = 'driver_licenses'
    
    id = db.Column(db.Integer, primary_key=True)
    dl_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points = db.Column(db.Integer, default=12)  # Starting points (12 is typical in India)
    status = db.Column(db.String(20), default='Active')  # Active, Suspended, Revoked
    issued_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    vehicle_class = db.Column(db.String(50))  # LMV, MCWG, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='driver_license')

class Appeal(db.Model):
    """Virtual Court Appeals"""
    __tablename__ = 'appeals'
    
    id = db.Column(db.Integer, primary_key=True)
    challan_id = db.Column(db.Integer, db.ForeignKey('challans.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewer_notes = db.Column(db.Text)
    
    # Relationships
    challan = db.relationship('Challan', backref='appeals')
    user = db.relationship('User', backref='appeals')

class PaymentPlan(db.Model):
    """Installment Payment Plans"""
    __tablename__ = 'payment_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    challan_id = db.Column(db.Integer, db.ForeignKey('challans.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    remaining_amount = db.Column(db.Float, nullable=False)
    installment_count = db.Column(db.Integer, default=1)
    current_installment = db.Column(db.Integer, default=0)
    next_due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Active')  # Active, Completed, Defaulted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    challan = db.relationship('Challan', backref='payment_plan')

# Add stolen vehicle fields to Vehicle model (if not already present)
# These would be added via migration in production
# For now, we'll handle them as optional attributes
