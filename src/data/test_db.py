import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.db_manager import DatabaseManager
from datetime import datetime

def test_database_operations():
    """Test basic database operations"""
    db = DatabaseManager()
    
    # Test 1: Add new appointment
    print("Testing appointment creation...")
    today = datetime.now().strftime("%Y-%m-%d")
    success = db.add_appointment(
        date=today,
        time="11:00",
        doctor="Dr. Test",
        notes="Test appointment"
    )
    print(f"Appointment creation {'successful' if success else 'failed'}")
    
    # Test 2: Check availability
    print("\nTesting availability check...")
    is_available = db.check_availability(today, "11:00")
    print(f"Time slot availability: {'available' if is_available else 'not available'}")
    
    # Test 3: Retrieve appointments
    print("\nTesting appointment retrieval...")
    appointments = db.get_appointments(today)
    print(f"Found {len(appointments)} appointments for today")
    
    # Test 4: Cancel appointment
    print("\nTesting appointment cancellation...")
    cancelled = db.cancel_appointment(today, "11:00")
    print(f"Appointment cancellation {'successful' if cancelled else 'failed'}")
    
    # Test 5: Update notes
    print("\nTesting note update...")
    updated = db.update_appointment_notes(today, "11:00", "Updated test notes")
    print(f"Note update {'successful' if updated else 'failed'}")

if __name__ == "__main__":
    print("Running database tests...\n")
    test_database_operations()
    print("\nDatabase tests complete!")