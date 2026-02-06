from datetime import datetime

from models import Challan, Violation, db


def calculate_fine(violation_type: str, vehicle_id: int):
    prev_count = (
        Challan.query.filter_by(vehicle_id=vehicle_id, violation_type=violation_type)
        .filter(Challan.created_at < datetime.utcnow())
        .count()
    )
    subsequent = prev_count > 0
    court_mandatory = False

    if violation_type == "No Helmet":
        base = 1000
        fine = base * 2 if subsequent else base
    elif violation_type == "Drunk Driving":
        fine = 0
        court_mandatory = True
    elif violation_type == "Signal Jumping":
        fine = 1000 if not subsequent else 5000
    elif violation_type == "Triple Riding":
        fine = 1000
    else:
        v = Violation.query.filter_by(violation_type=violation_type).first()
        fine = v.fine_amount if v else 1000

    return fine, subsequent, court_mandatory

