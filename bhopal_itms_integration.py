"""
Bhopal ITMS Integration Module
Based on Bhopal Smart City's Intelligent Traffic Management System
Features: No Helmet Detection, Vehicle Classification, Suspected Vehicle Detection
"""

from datetime import datetime
from models import Vehicle, Challan, db
from advanced_detection_services import EdgeAnalyticsService, ANPRService

class BhopalITMSService:
    """Bhopal ITMS Integration Service"""
    
    @staticmethod
    def detect_no_helmet_violation(image_path, license_number=None):
        """
        Bhopal ITMS No Helmet Detection
        First ever "No Helmet Detection" technology in India
        Detects:
        - Driver without helmet
        - Driver wearing cap but not helmet
        - Driver wearing scarf but without helmet
        - Passenger without helmet
        """
        # Use Edge Analytics Service
        result = EdgeAnalyticsService.detect_helmet_violation(image_path, '2-wheeler')
        
        violations = []
        for violation in result.get('violations', []):
            challan_data = {
                'violation_type': violation['violation_type'],
                'sub_type': violation.get('sub_type', ''),
                'person': violation.get('person', 'driver'),
                'confidence': violation['confidence'],
                'license_number': license_number,
                'timestamp': violation['timestamp']
            }
            violations.append(challan_data)
        
        return {
            'violations': violations,
            'total_detected': len(violations),
            'vehicle_type': result.get('vehicle_type'),
            'image_path': image_path
        }
    
    @staticmethod
    def classify_and_detect(image_path):
        """
        Classify vehicle and detect all possible violations
        Based on Bhopal ITMS classification system
        """
        # Classify vehicle
        vehicle_class = EdgeAnalyticsService.classify_vehicle(image_path)
        
        violations = []
        
        # Detect violations based on vehicle class
        if vehicle_class['vehicle_class'] == '2-wheeler':
            # Check for helmet violations
            helmet_result = EdgeAnalyticsService.detect_helmet_violation(image_path, '2-wheeler')
            violations.extend(helmet_result.get('violations', []))
            
            # Check for triple riding
            triple_riding = EdgeAnalyticsService.detect_triple_riding(image_path)
            if triple_riding:
                violations.append(triple_riding)
        
        # Check for wrong way
        wrong_way = EdgeAnalyticsService.detect_wrong_way(image_path, 'forward')
        if wrong_way:
            violations.append(wrong_way)
        
        # Check for stopped on road
        stopped = EdgeAnalyticsService.detect_vehicle_stopping_on_road(image_path, 'green')
        if stopped:
            violations.append(stopped)
        
        return {
            'vehicle_class': vehicle_class,
            'violations': violations,
            'total_violations': len(violations)
        }
    
    @staticmethod
    def check_suspected_vehicle(license_number):
        """
        Check if vehicle is in suspected vehicle list
        Based on Bhopal ITMS Suspected Vehicle Detection
        """
        vehicle = Vehicle.query.filter_by(license_number=license_number).first()
        
        if not vehicle:
            return {
                'is_suspected': False,
                'license_number': license_number,
                'message': 'Vehicle not found in database'
            }
        
        # Check various flags
        is_suspected = getattr(vehicle, 'is_stolen', False) or \
                      getattr(vehicle, 'is_blacklisted', False) or \
                      getattr(vehicle, 'is_wanted', False)
        
        if is_suspected:
            # Generate alert at control room
            alert_data = {
                'is_suspected': True,
                'license_number': license_number,
                'alert_level': 'high',
                'reason': 'Vehicle in suspected list',
                'timestamp': datetime.now().isoformat(),
                'action': 'notify_control_room'
            }
            
            # In production, this would send alert to control room
            BhopalITMSService.notify_control_room(alert_data)
            
            return alert_data
        
        return {
            'is_suspected': False,
            'license_number': license_number
        }
    
    @staticmethod
    def notify_control_room(alert_data):
        """
        Send alert to control room (Bhopal ITMS Feature)
        In production, this would integrate with command center
        """
        # Mock implementation - would send to control room dashboard
        print(f"[CONTROL ROOM ALERT] Suspected Vehicle: {alert_data['license_number']}")
        print(f"Alert Level: {alert_data['alert_level']}")
        print(f"Timestamp: {alert_data['timestamp']}")
        
        # Would also send to PA System, Variable Message Signs, etc.
        return True
    
    @staticmethod
    def generate_statistics(time_period='24h'):
        """
        Generate statistical analysis (Bhopal ITMS Feature)
        Classify violations by vehicle type and generate statistics
        """
        from datetime import timedelta
        
        if time_period == '24h':
            start_time = datetime.now() - timedelta(hours=24)
        elif time_period == '7d':
            start_time = datetime.now() - timedelta(days=7)
        else:
            start_time = datetime.now() - timedelta(days=30)
        
        challans = Challan.query.filter(
            Challan.created_at >= start_time
        ).all()
        
        # Classify by vehicle type
        stats = {
            '2-wheeler': {
                'total': 0,
                'no_helmet': 0,
                'triple_riding': 0,
                'other': 0
            },
            '4-wheeler': {
                'total': 0,
                'red_light': 0,
                'speeding': 0,
                'other': 0
            },
            'auto-rickshaw': {
                'total': 0,
                'violations': []
            },
            'heavy-vehicle': {
                'total': 0,
                'overloading': 0,
                'other': 0
            }
        }
        
        for challan in challans:
            violation_type = challan.violation_type
            
            # Classify based on violation type
            if 'Helmet' in violation_type or 'Triple' in violation_type:
                stats['2-wheeler']['total'] += 1
                if 'Helmet' in violation_type:
                    stats['2-wheeler']['no_helmet'] += 1
                elif 'Triple' in violation_type:
                    stats['2-wheeler']['triple_riding'] += 1
                else:
                    stats['2-wheeler']['other'] += 1
            elif 'Red Light' in violation_type or 'Signal' in violation_type:
                stats['4-wheeler']['total'] += 1
                stats['4-wheeler']['red_light'] += 1
            elif 'Speeding' in violation_type:
                stats['4-wheeler']['total'] += 1
                stats['4-wheeler']['speeding'] += 1
            elif 'Overloading' in violation_type:
                stats['heavy-vehicle']['total'] += 1
                stats['heavy-vehicle']['overloading'] += 1
        
        return {
            'time_period': time_period,
            'start_time': start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_challans': len(challans),
            'statistics': stats
        }
    
    @staticmethod
    def integrate_with_rto(license_number):
        """
        Integrate with RTO database (Bhopal ITMS Feature)
        Auto email challan, payment portal integration
        """
        vehicle = Vehicle.query.filter_by(license_number=license_number).first()
        
        if not vehicle:
            return {
                'success': False,
                'message': 'Vehicle not found in database'
            }
        
        # In production, this would query RTO/Vahan database
        rto_data = {
            'license_number': license_number,
            'owner_name': vehicle.owner.name if vehicle.owner else 'N/A',
            'owner_email': vehicle.owner.email if vehicle.owner else 'N/A',
            'owner_phone': vehicle.owner.phone if vehicle.owner else 'N/A',
            'vehicle_model': vehicle.model,
            'registration_date': vehicle.registration_date.isoformat() if vehicle.registration_date else None,
            'insurance_expiry': vehicle.insurance_expiry.isoformat() if vehicle.insurance_expiry else None,
            'rto_code': getattr(vehicle, 'rto_code', None)
        }
        
        return {
            'success': True,
            'rto_data': rto_data,
            'integration_status': 'connected'
        }
    
    @staticmethod
    def auto_email_challan(challan_id):
        """
        Auto email challan to vehicle owner (Bhopal ITMS Feature)
        """
        challan = Challan.query.get(challan_id)
        if not challan:
            return {'success': False, 'message': 'Challan not found'}
        
        vehicle = challan.vehicle
        owner = vehicle.owner if vehicle else None
        
        if not owner or not owner.email:
            return {'success': False, 'message': 'Owner email not found'}
        
        # In production, this would send email
        email_data = {
            'to': owner.email,
            'subject': f'E-Challan #{challan.id} - {challan.violation_type}',
            'body': f"""
            Dear {owner.name or 'Vehicle Owner'},
            
            An E-Challan has been issued for your vehicle {vehicle.license_number}.
            
            Violation: {challan.violation_type}
            Fine Amount: ₹{challan.fine_amount}
            Location: {challan.location or 'N/A'}
            Date: {challan.created_at.strftime('%Y-%m-%d %H:%M')}
            UIN: {challan.uin or 'N/A'}
            
            Please pay the fine online at: https://echallan.mponline.gov.in/ui/common.html
            
            Thank you,
            AutoFINE System
            """
        }
        
        # Mock email sending
        print(f"[EMAIL] Sending challan to {owner.email}")
        print(f"Subject: {email_data['subject']}")
        
        return {
            'success': True,
            'email_sent': True,
            'recipient': owner.email
        }

# Export service
__all__ = ['BhopalITMSService']
