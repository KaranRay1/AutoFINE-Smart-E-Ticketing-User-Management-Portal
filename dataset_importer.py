"""
Comprehensive Dataset Importer for AutoFINE
Handles multiple CSV formats and integrates them into the database
"""

import csv
import os
from datetime import datetime, timedelta
import random
import uuid
from models import db, User, Vehicle, Challan, Violation, Camera
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

INDIAN_SAMPLE_NAMES = [
    "Aarav Sharma", "Vihaan Verma", "Aditya Singh", "Arjun Kumar", "Ishaan Gupta",
    "Rohan Mehta", "Kunal Joshi", "Siddharth Rana", "Ananya Sharma", "Priya Singh",
    "Neha Verma", "Kritika Gupta", "Sneha Joshi", "Riya Mehta", "Pooja Rawat",
    "Rahul Negi", "Nitin Bhatt", "Deepak Chauhan", "Manish Bisht", "Vikram Thakur",
    "Kavita Joshi", "Shreya Singh", "Tanya Verma", "Aditi Gupta", "Sakshi Mehta",
]

class DatasetImporter:
    """Import various CSV datasets into AutoFINE database"""
    
    def __init__(self, app):
        self.app = app
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def import_punjab_challan_dataset(self, csv_path=None):
        """
        Import Punjab E-Challan Dataset (500 rows)
        Format: challan_id, vehicle_type, violation_type, location, city, violation_time, 
                speed_recorded_kmph, fine_amount_PKR, payment_status, issuing_method, repeat_offender
        """
        if not csv_path:
            csv_path = os.path.join(self.base_path, 'archive', 'Punjab_E_Challan_Dataset_500_Rows.csv')
        
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return 0
        
        imported = 0
        
        with self.app.app_context():
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                owners = User.query.filter_by(user_type='owner').all()
                
                if not owners:
                    # Create default owners if none exist
                    for i in range(20):
                        full_name = INDIAN_SAMPLE_NAMES[i % len(INDIAN_SAMPLE_NAMES)]
                        uname = full_name.lower().replace(" ", "_") + f"_{i+1}"
                        owner = User(
                            username=uname,
                            email=f'{uname}@example.com',
                            password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
                            user_type='owner',
                            phone=f'98765432{i:02d}',
                            dl_number=f"UKDL-{random.randint(10,99)}-{random.randint(100000,999999)}"
                        )
                        db.session.add(owner)
                    db.session.commit()
                    owners = User.query.filter_by(user_type='owner').all()
                
                vehicles_created = {}
                
                for row in reader:
                    try:
                        # Convert vehicle type to license plate format
                        vehicle_type = row.get('vehicle_type', 'Car')
                        city = row.get('city', 'Unknown')
                        
                        # Generate or use existing license number
                        license_number = self._generate_license_number(vehicle_type, city)
                        
                        if license_number not in vehicles_created:
                            # Create vehicle
                            owner = random.choice(owners)
                            vehicle = Vehicle(
                                license_number=license_number,
                                owner_id=owner.id,
                                model=vehicle_type,
                                registration_date=datetime.now() - timedelta(days=random.randint(30, 1825)),
                                insurance_expiry=datetime.now() + timedelta(days=random.randint(30, 365)),
                                city=city,
                                state="Uttarakhand"
                            )
                            db.session.add(vehicle)
                            db.session.flush()
                            vehicles_created[license_number] = vehicle
                        else:
                            vehicle = vehicles_created[license_number]
                        
                        # Create challan
                        violation_type = row.get('violation_type', 'Unknown')
                        fine_amount_pkr = float(row.get('fine_amount_PKR', 0) or 0)
                        # Convert PKR to INR (approximate 1:1 for demo, adjust as needed)
                        fine_amount = fine_amount_pkr
                        
                        payment_status = row.get('payment_status', 'Unpaid')
                        status = 'Paid' if payment_status == 'Paid' else 'Unpaid'
                        
                        challan = Challan(
                            vehicle_id=vehicle.id,
                            uin=f"UIN-{row.get('challan_id', 'UNK')}",
                            violation_type=violation_type,
                            location=row.get('location', 'Unknown'),
                            fine_amount=fine_amount,
                            status=status,
                            created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
                            due_date=datetime.now() + timedelta(days=random.randint(1, 30)),
                            evidence_image=None,
                            is_subsequent=row.get('repeat_offender', 'No') == 'Yes'
                        )
                        
                        if status == 'Paid':
                            challan.paid_at = challan.created_at + timedelta(days=random.randint(1, 15))
                        
                        db.session.add(challan)
                        imported += 1
                        
                        if imported % 50 == 0:
                            db.session.commit()
                            print(f"Imported {imported} challans...")
                    
                    except Exception as e:
                        print(f"Error importing row: {e}")
                        continue
                
                db.session.commit()
                print(f"✓ Imported {imported} challans from Punjab dataset")
                return imported
    
    def import_state_statistics(self, csv_path):
        """
        Import state/district-wise challan statistics
        Format: Year, State, District, Total Challans, Total Challan Amount, Total Revenue Collected
        """
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return 0
        
        imported = 0
        
        with self.app.app_context():
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        state = row.get('State', '')
                        district = row.get('District', '')
                        total_challans = int(row.get('Total Challans', 0) or 0)
                        total_amount = float(row.get('Total Challan Amount', 0) or 0)
                        revenue = float(row.get('Total Revenue Collected', 0) or 0)
                        
                        # Store statistics (could create a Statistics model)
                        # For now, we'll just log it
                        print(f"State: {state}, District: {district}, Challans: {total_challans}, Amount: ₹{total_amount:,.0f}")
                        imported += 1
                    
                    except Exception as e:
                        print(f"Error importing statistics row: {e}")
                        continue
                
                print(f"✓ Processed {imported} state statistics records")
                return imported
    
    def import_offence_statistics(self, csv_path):
        """
        Import offence-wise statistics
        Format: Sl. No., State/UT, Offence, Total Number of Challan, Revenue Collected
        """
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return 0
        
        imported = 0
        
        with self.app.app_context():
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        state = row.get('State/UT', '')
                        offence = row.get('Offence', '')
                        total_challans = int(row.get('Total Number of Challan', 0) or 0)
                        revenue = float(row.get('Revenue Collected (In Rupees)', 0) or 0)
                        
                        # Extract violation type from offence description
                        violation_type = self._extract_violation_type(offence)
                        
                        # Update or create violation entry
                        violation = Violation.query.filter_by(violation_type=violation_type).first()
                        if not violation:
                            avg_fine = revenue / total_challans if total_challans > 0 else 1000
                            violation = Violation(
                                violation_type=violation_type,
                                fine_amount=avg_fine
                            )
                            db.session.add(violation)
                            imported += 1
                    
                    except Exception as e:
                        print(f"Error importing offence row: {e}")
                        continue
                
                db.session.commit()
                print(f"✓ Imported {imported} offence types")
                return imported
    
    def import_indian_traffic_violations(self, csv_path=None):
        """
        Import Indian Traffic Violations Dataset
        Comprehensive dataset with detailed violation information
        """
        if not csv_path:
            csv_path = os.path.join(self.base_path, 'data', 'Indian_Traffic_Violations.csv')
        
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return 0
        
        imported = 0
        
        with self.app.app_context():
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                owners = User.query.filter_by(user_type='owner').all()
                
                if not owners:
                    for i in range(20):
                        owner = User(
                            username=f'owner{i+1}',
                            email=f'owner{i+1}@example.com',
                            password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
                            user_type='owner',
                            phone=f'98765432{i:02d}',
                            dl_number=f'DL-{random.randint(100000, 999999)}'
                        )
                        db.session.add(owner)
                    db.session.commit()
                    owners = User.query.filter_by(user_type='owner').all()
                
                vehicles_created = {}
                
                for row in reader:
                    try:
                        # Extract data
                        violation_type = row.get('Violation_Type', 'Unknown')
                        location = row.get('Location', 'Unknown')
                        registration_state = row.get('Registration_State', 'Uttarakhand')
                        vehicle_type = row.get('Vehicle_Type', 'Car')
                        vehicle_color = row.get('Vehicle_Color', 'Unknown')
                        fine_amount = float(row.get('Fine_Amount', 0) or 0)
                        
                        # Convert to INR if needed (assuming already in INR)
                        if fine_amount < 100:  # Likely in different currency, convert
                            fine_amount = fine_amount * 50  # Approximate conversion
                        
                        # Parse date and time
                        date_str = row.get('Date', '')
                        time_str = row.get('Time', '')
                        try:
                            if date_str:
                                created_at = datetime.strptime(date_str, '%Y-%m-%d')
                                if time_str:
                                    try:
                                        time_obj = datetime.strptime(time_str, '%H:%M').time()
                                        created_at = datetime.combine(created_at.date(), time_obj)
                                    except:
                                        pass
                            else:
                                created_at = datetime.now() - timedelta(days=random.randint(1, 365))
                        except:
                            created_at = datetime.now() - timedelta(days=random.randint(1, 365))
                        
                        # Generate or use existing license number
                        city = location if location else 'Dehradun'
                        license_number = self._generate_license_number_from_state(registration_state, city, vehicle_type)
                        
                        if license_number not in vehicles_created:
                            owner = random.choice(owners)
                            vehicle_data = {
                                'license_number': license_number,
                                'owner_id': owner.id,
                                'model': f"{vehicle_type} {vehicle_color}",
                                'registration_date': created_at - timedelta(days=random.randint(30, 1825)),
                                'insurance_expiry': datetime.now() + timedelta(days=random.randint(30, 365)),
                                'city': city,
                                'state': registration_state
                            }
                            # Only add rto_code if Vehicle model supports it
                            try:
                                vehicle = Vehicle(**vehicle_data, rto_code=self._get_rto_code(city))
                            except TypeError:
                                vehicle = Vehicle(**vehicle_data)
                            db.session.add(vehicle)
                            db.session.flush()
                            vehicles_created[license_number] = vehicle
                        else:
                            vehicle = vehicles_created[license_number]
                        
                        # Determine status
                        fine_paid = row.get('Fine_Paid', 'No')
                        status = 'Paid' if fine_paid == 'Yes' else 'Unpaid'
                        
                        # Check if court appearance required
                        court_required = row.get('Court_Appearance_Required', 'No')
                        if court_required == 'Yes' or violation_type == 'Drunk Driving':
                            status = 'Court'
                        
                        # Create challan
                        uin = f"UIN-{uuid.uuid4().hex[:12].upper()}"
                        challan = Challan(
                            vehicle_id=vehicle.id,
                            uin=uin,
                            violation_type=violation_type,
                            location=location,
                            fine_amount=fine_amount,
                            status=status,
                            created_at=created_at,
                            due_date=created_at + timedelta(days=30),
                            evidence_image=None,
                            is_subsequent=row.get('Previous_Violations', '0') != '0' and int(row.get('Previous_Violations', 0) or 0) > 0
                        )
                        
                        if status == 'Paid':
                            challan.paid_at = created_at + timedelta(days=random.randint(1, 15))
                        
                        db.session.add(challan)
                        imported += 1
                        
                        if imported % 100 == 0:
                            db.session.commit()
                            print(f"Imported {imported} violations...")
                    
                    except Exception as e:
                        print(f"Error importing violation row: {e}")
                        continue
                
                db.session.commit()
                print(f"✓ Imported {imported} violations from Indian Traffic Violations dataset")
                return imported
    
    def import_traffic_flow_data(self, csv_path=None):
        """
        Import Traffic Flow Data (DateTime, Junction, Vehicles)
        This data can be used for analytics and traffic pattern analysis
        """
        if not csv_path:
            csv_path = os.path.join(self.base_path, 'data', 'traffic.csv')
        
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return 0
        
        imported = 0
        
        with self.app.app_context():
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Store traffic flow data (could create a TrafficFlow model)
                # For now, we'll use it to create cameras at junctions
                junctions_processed = set()
                
                for row in reader:
                    try:
                        junction = row.get('Junction', '')
                        vehicles_count = int(row.get('Vehicles', 0) or 0)
                        datetime_str = row.get('DateTime', '')
                        
                        if junction and junction not in junctions_processed:
                            # Create camera at junction if not exists
                            camera = Camera.query.filter_by(location=f"Junction {junction}").first()
                            if not camera:
                                camera = Camera(
                                    location=f"Junction {junction}",
                                    camera_type='Traffic Monitor',
                                    is_active=True
                                )
                                db.session.add(camera)
                                junctions_processed.add(junction)
                                imported += 1
                        
                        if imported % 10 == 0 and imported > 0:
                            db.session.commit()
                    
                    except Exception as e:
                        continue
                
                db.session.commit()
                print(f"✓ Processed {imported} traffic junctions from traffic flow data")
                return imported
    
    def import_police_stop_data(self, csv_path=None):
        """
        Import Police Stop Data
        This can be used to understand traffic enforcement patterns
        """
        if not csv_path:
            csv_path = os.path.join(self.base_path, 'data', 'police.csv')
        
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return 0
        
        imported = 0
        
        with self.app.app_context():
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        violation = row.get('violation', '')
                        stop_outcome = row.get('stop_outcome', '')
                        is_arrested = row.get('is_arrested', 'False') == 'True'
                        
                        # Extract violation type
                        violation_type = self._extract_violation_type(violation)
                        
                        # Update violation statistics
                        violation_entry = Violation.query.filter_by(violation_type=violation_type).first()
                        if not violation_entry:
                            violation_entry = Violation(
                                violation_type=violation_type,
                                fine_amount=1000  # Default fine
                            )
                            db.session.add(violation_entry)
                            imported += 1
                    
                    except Exception as e:
                        continue
                
                db.session.commit()
                print(f"✓ Processed {imported} violation types from police stop data")
                return imported
    
    def import_all_datasets(self):
        """Import all available datasets"""
        print("=" * 60)
        print("Starting Comprehensive Dataset Import")
        print("=" * 60)
        
        total_imported = 0
        
        # 1. Indian Traffic Violations Dataset (comprehensive)
        indian_violations_path = os.path.join(self.base_path, 'data', 'Indian_Traffic_Violations.csv')
        if os.path.exists(indian_violations_path):
            print("\n[1/8] Importing Indian Traffic Violations Dataset...")
            total_imported += self.import_indian_traffic_violations(indian_violations_path)
        
        # 2. Traffic Flow Data
        traffic_flow_path = os.path.join(self.base_path, 'data', 'traffic.csv')
        if os.path.exists(traffic_flow_path):
            print("\n[2/8] Processing Traffic Flow Data...")
            total_imported += self.import_traffic_flow_data(traffic_flow_path)
        
        # 3. Police Stop Data
        police_stop_path = os.path.join(self.base_path, 'data', 'police.csv')
        if os.path.exists(police_stop_path):
            print("\n[3/8] Processing Police Stop Data...")
            total_imported += self.import_police_stop_data(police_stop_path)
        
        # 4. Punjab Challan Dataset (individual records)
        punjab_path = os.path.join(self.base_path, 'archive', 'Punjab_E_Challan_Dataset_500_Rows.csv')
        if os.path.exists(punjab_path):
            print("\n[4/8] Importing Punjab E-Challan Dataset...")
            total_imported += self.import_punjab_challan_dataset(punjab_path)
        
        # 5. State/District Statistics
        state_stats_path = os.path.join(self.base_path, 'dataset', 'RS_Session_259_AU_1689_A.csv')
        if os.path.exists(state_stats_path):
            print("\n[5/8] Processing State/District Statistics...")
            self.import_state_statistics(state_stats_path)
        
        # 6. Offence Statistics
        offence_stats_path = os.path.join(self.base_path, 'dataset', 'RS_Session_267_AU_2175_A_and_C.csv')
        if os.path.exists(offence_stats_path):
            print("\n[6/8] Importing Offence Statistics...")
            total_imported += self.import_offence_statistics(offence_stats_path)
        
        # 7. Yearly Statistics
        yearly_stats_path = os.path.join(self.base_path, 'dataset', 'RS_Session_256_AU_93_D.csv')
        if os.path.exists(yearly_stats_path):
            print("\n[7/8] Processing Yearly Statistics...")
            self.import_state_statistics(yearly_stats_path)
        
        # 8. State-wise Revenue Statistics
        revenue_stats_path = os.path.join(self.base_path, 'dataset', 'RS_Session_266_AU_1849_E_i.csv')
        if os.path.exists(revenue_stats_path):
            print("\n[8/8] Processing State Revenue Statistics...")
            self.import_state_statistics(revenue_stats_path)
        
        print("\n" + "=" * 60)
        print(f"✓ Dataset Import Complete! Total records imported: {total_imported}")
        print("=" * 60)
        
        return total_imported
    
    def _generate_license_number(self, vehicle_type, city):
        """Generate Indian-style license number"""
        # Map cities to RTO codes
        city_rto_map = {
            'Lahore': '01', 'Rawalpindi': '02', 'Faisalabad': '03',
            'Delhi': '01', 'Mumbai': '01', 'Bangalore': '02',
            'Dehradun': '07', 'Nainital': '06', 'Almora': '01'
        }
        
        rto_code = city_rto_map.get(city, '01')
        state_code = 'UK'  # Uttarakhand
        
        # Generate random alphanumeric
        import string
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        numbers = ''.join(random.choices(string.digits, k=4))
        
        return f"{state_code}-{rto_code}-{letters}-{numbers}"
    
    def _get_rto_code(self, city):
        """Get RTO code for city"""
        city_rto_map = {
            'Lahore': '01', 'Rawalpindi': '02', 'Faisalabad': '03',
            'Delhi': '01', 'Mumbai': '01', 'Bangalore': '02',
            'Dehradun': '07', 'Nainital': '06', 'Almora': '01', 'Khatima': '14'
        }
        return city_rto_map.get(city, '01')
    
    def _generate_license_number_from_state(self, state, city, vehicle_type):
        """Generate license number based on state and city"""
        # Map states to state codes
        state_code_map = {
            'Uttarakhand': 'UK', 'Delhi': 'DL', 'Maharashtra': 'MH',
            'Karnataka': 'KA', 'Punjab': 'PB', 'West Bengal': 'WB',
            'Tamil Nadu': 'TN', 'Gujarat': 'GJ', 'Uttar Pradesh': 'UP'
        }
        
        state_code = state_code_map.get(state, 'UK')
        rto_code = self._get_rto_code(city)
        
        import string
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        numbers = ''.join(random.choices(string.digits, k=4))
        
        return f"{state_code}-{rto_code}-{letters}-{numbers}"
    
    def _extract_violation_type(self, offence_description):
        """Extract violation type from offence description"""
        if not offence_description:
            return 'Unknown'
        
        offence_lower = offence_description.lower()
        
        if 'helmet' in offence_lower:
            return 'No Helmet'
        elif 'speeding' in offence_lower or 'speed' in offence_lower or 'over-speeding' in offence_lower:
            return 'Speeding'
        elif 'signal' in offence_lower or 'red light' in offence_lower:
            return 'Signal Jumping'
        elif 'parking' in offence_lower:
            return 'Wrong Parking'
        elif 'minor' in offence_lower or 'under-aged' in offence_lower:
            return 'Under-aged Driving'
        elif 'drunk' in offence_lower or 'alcohol' in offence_lower or 'dwi' in offence_lower:
            return 'Drunk Driving'
        elif 'license' in offence_lower or 'driving without license' in offence_lower:
            return 'No License'
        elif 'triple' in offence_lower:
            return 'Triple Riding'
        elif 'seatbelt' in offence_lower or 'seat belt' in offence_lower:
            return 'No Seatbelt'
        elif 'mobile' in offence_lower or 'phone' in offence_lower:
            return 'Using Mobile Phone'
        elif 'overloading' in offence_lower:
            return 'Overloading'
        else:
            # Return first few words as violation type
            words = offence_description.split()[:3]
            return ' '.join(words) if words else 'Unknown'
