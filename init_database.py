"""
Database Initialization Script
Creates tables and populates with sample data from CSV
"""

from app import app, db, bcrypt
from models import User, Vehicle, Challan, Violation, Camera, Notice
from datetime import datetime, timedelta
import csv
import random
import os
import uuid

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(
                username='admin',
                email='admin@autofine.com',
                phone='+91-9876543210',
                password_hash=admin_password,
                user_type='admin'
            )
            db.session.add(admin)
            print("Created admin user (username: admin, password: admin123)")
        
        # Create sample vehicle owners
        sample_owners = [
            {'username': 'john_doe', 'email': 'john@example.com', 'phone': '+91-9876543211'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'phone': '+91-9876543212'},
            {'username': 'rahul_kumar', 'email': 'rahul@example.com', 'phone': '+91-9876543213'},
        ]

        # Add many unique owner names (demo realistic dataset)
        extra_names = [
            "Aarav Sharma","Vihaan Verma","Aditya Singh","Arjun Kumar","Ishaan Gupta","Rohan Mehta",
            "Kunal Joshi","Siddharth Rana","Rahul Negi","Nitin Bhatt","Deepak Chauhan","Manish Bisht",
            "Vikram Thakur","Amit Rawat","Saurabh Pant","Rakesh Joshi","Pradeep Singh","Mohit Verma",
            "Sandeep Kumar","Dinesh Gupta","Neha Sharma","Ananya Singh","Priya Verma","Kritika Gupta",
            "Sneha Joshi","Riya Mehta","Pooja Rawat","Shreya Singh","Aditi Gupta","Sakshi Mehta",
        ]
        for i, full in enumerate(extra_names, start=1):
            uname = full.lower().replace(" ", "_") + f"_{i}"
            sample_owners.append({
                'username': uname,
                'email': f'{uname}@example.com',
                'phone': f'+91-98{random.randint(10000000,99999999)}'
            })
        
        for owner_data in sample_owners:
            if not User.query.filter_by(username=owner_data['username']).first():
                password_hash = bcrypt.generate_password_hash('password123').decode('utf-8')
                owner = User(
                    username=owner_data['username'],
                    email=owner_data['email'],
                    phone=owner_data['phone'],
                    dl_number=f"UKDL-{random.randint(10,99)}-{random.randint(100000,999999)}",
                    password_hash=password_hash,
                    user_type='owner'
                )
                db.session.add(owner)
        
        db.session.commit()
        print("Created sample vehicle owners")
        
        # Initialize violation types
        violations_data = [
            {'type': 'Speeding', 'fine': 1000},
            {'type': 'Signal Jumping', 'fine': 500},
            {'type': 'Wrong Parking', 'fine': 1500},
            {'type': 'No Helmet', 'fine': 500},
            {'type': 'Red Light Violation', 'fine': 1000},
            {'type': 'Wrong Lane', 'fine': 750},
            {'type': 'Overloading', 'fine': 2000}
        ]
        
        for v in violations_data:
            if not Violation.query.filter_by(violation_type=v['type']).first():
                violation = Violation(
                    violation_type=v['type'],
                    fine_amount=v['fine']
                )
                db.session.add(violation)
        
        db.session.commit()
        print("Initialized violation types")
        
        # Initialize cameras
        cameras_data = [
            {'camera_id': 'CAM001', 'location': 'Main Street, Signal 1', 'lat': 28.7041, 'lon': 77.1025},
            {'camera_id': 'CAM002', 'location': 'Highway Road, Toll Plaza', 'lat': 28.6141, 'lon': 77.2025},
            {'camera_id': 'CAM003', 'location': 'Downtown, Signal 5', 'lat': 28.8041, 'lon': 77.3025},
        ]
        
        for cam_data in cameras_data:
            if not Camera.query.filter_by(camera_id=cam_data['camera_id']).first():
                camera = Camera(
                    camera_id=cam_data['camera_id'],
                    location=cam_data['location'],
                    latitude=cam_data['lat'],
                    longitude=cam_data['lon'],
                    is_active=True
                )
                db.session.add(camera)
        
        db.session.commit()
        print("Initialized cameras")

        # Seed notices (State/Central)
        if Notice.query.count() == 0:
            notices = [
                {"scope": "Central", "title": "Road Safety Advisory (MoRTH)", "body": "Wear helmet/seatbelt. Follow speed limits. Use valid documents.", "state": None, "city": None},
                {"scope": "State", "title": "Uttarakhand Traffic Notice", "body": "E-challan enforcement active at entry points and major junctions. Keep RC/Insurance/PUC valid.", "state": "Uttarakhand", "city": None},
                {"scope": "State", "title": "Dehradun Traffic Update", "body": "Signal jumping enforcement intensified at key crossings.", "state": "Uttarakhand", "city": "Dehradun"},
            ]
            for n in notices:
                db.session.add(Notice(**n))
            db.session.commit()
            print("Seeded traffic notices")
        
        # Load vehicles and challans from CSV if available
        try:
            # Try multiple possible paths
            csv_paths = [
                '../archive/Punjab_E_Challan_Dataset_500_Rows.csv',
                '../../archive/Punjab_E_Challan_Dataset_500_Rows.csv',
                'archive/Punjab_E_Challan_Dataset_500_Rows.csv'
            ]
            csv_path = None
            for path in csv_paths:
                if os.path.exists(path):
                    csv_path = path
                    break
            
            if not csv_path:
                raise FileNotFoundError("CSV file not found")
            vehicles_created = set()
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                owners = User.query.filter_by(user_type='owner').all()
                
                for row in reader:
                    # Generate unique license number
                    max_attempts = 10
                    license_number = None
                    for _ in range(max_attempts):
                        candidate = f"PB-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
                        if candidate not in vehicles_created and not Vehicle.query.filter_by(license_number=candidate).first():
                            license_number = candidate
                            break
                    
                    if not license_number:
                        continue  # Skip if couldn't generate unique number
                    
                    # Create vehicle if not exists
                    if license_number not in vehicles_created:
                        vehicle = Vehicle(
                            license_number=license_number,
                            owner_id=random.choice(owners).id if owners else 1,
                            vehicle_type=row.get('vehicle_type', 'Car'),
                            model=row.get('vehicle_type', 'Unknown'),
                            state="Uttarakhand",
                            city=random.choice(["Dehradun","Haldwani","Almora","Khatima"]),
                            registration_date=datetime.now() - timedelta(days=random.randint(365, 3650)),
                            insurance_expiry=datetime.now().date() + timedelta(days=random.randint(30, 365))
                        )
                        db.session.add(vehicle)
                        db.session.flush()
                        vehicles_created.add(license_number)
                        
                        # Get vehicle ID
                        vehicle_id = vehicle.id
                    else:
                        vehicle = Vehicle.query.filter_by(license_number=license_number).first()
                        vehicle_id = vehicle.id if vehicle else None
                    
                    if vehicle_id:
                        # Create challan
                        violation_type = row.get('violation_type', 'Speeding')
                        fine_amount = float(row.get('fine_amount_PKR', 1000))
                        location = row.get('location', 'Unknown')
                        payment_status = row.get('payment_status', 'Unpaid')
                        
                        # Parse violation time
                        violation_time = row.get('violation_time', 'Morning')
                        
                        challan = Challan(
                            vehicle_id=vehicle_id,
                            uin=f"UIN-{uuid.uuid4().hex[:12].upper()}",
                            violation_type=violation_type,
                            location=location,
                            fine_amount=fine_amount,
                            camera_id=1,
                            status='Paid' if payment_status == 'Paid' else 'Unpaid',
                            created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
                            due_date=datetime.now().date() + timedelta(days=random.randint(1, 30))
                        )
                        db.session.add(challan)
            
            db.session.commit()
            print(f"Loaded data from CSV - Created {len(vehicles_created)} vehicles")
        except FileNotFoundError:
            print("CSV file not found, skipping CSV import")
            # Create some sample vehicles manually
            owners = User.query.filter_by(user_type='owner').all()
            if owners:
                sample_vehicles = [
                    {'license': 'DL01AB1234', 'model': 'Maruti Swift', 'type': 'Car'},
                    {'license': 'DL02CD5678', 'model': 'Honda Activa', 'type': 'Bike'},
                    {'license': 'DL03EF9012', 'model': 'Toyota Innova', 'type': 'Car'},
                ]
                
                for v_data in sample_vehicles:
                    if not Vehicle.query.filter_by(license_number=v_data['license']).first():
                        vehicle = Vehicle(
                            license_number=v_data['license'],
                            owner_id=owners[0].id,
                            model=v_data['model'],
                            vehicle_type=v_data['type'],
                            registration_date=datetime.now() - timedelta(days=1000),
                            insurance_expiry=datetime.now().date() + timedelta(days=180)
                        )
                        db.session.add(vehicle)
                
                db.session.commit()
                print("Created sample vehicles")
        
        # Import all datasets using DatasetImporter
        try:
            from dataset_importer import DatasetImporter
            print("\n" + "="*60)
            print("Importing all available datasets...")
            print("="*60)
            importer = DatasetImporter(app)
            importer.import_all_datasets()
        except Exception as e:
            print(f"Error importing datasets: {e}")
            print("Continuing with basic initialization...")
        
        print("\nDatabase initialization complete!")
        print("\nDefault credentials:")
        print("  Admin: username=admin, password=admin123")
        print("  Owners: username=john_doe/jane_smith/rahul_kumar, password=password123")

if __name__ == '__main__':
    init_database()
