import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.db_manager import DatabaseManager
from datetime import datetime, timedelta

def initialize_database():
    """Initialize the database with sample data"""
    # Create database manager instance
    db = DatabaseManager()
    
    # Get today's date for sample data
    today = datetime.now()
    
    # Sample doctors
    doctors = [
        "Dr. Smith (General Physician)",
        "Dr. Johnson (Cardiologist)",
        "Dr. Williams (Pediatrician)",
        "Dr. Brown (Dermatologist)"
    ]
    
    # Sample appointments for the next 7 days
    for i in range(7):
        date = today + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # Add some appointments throughout the day
        appointments = [
            ("09:00", doctors[0], "Annual checkup"),
            ("10:30", doctors[1], "Heart consultation"),
            ("14:00", doctors[2], "Pediatric checkup"),
            ("15:30", doctors[3], "Skin examination")
        ]
        
        # Add appointments to database
        for time, doctor, notes in appointments:
            # Only add if the slot is available
            if db.check_availability(date_str, time):
                db.add_appointment(
                    date=date_str,
                    time=time,
                    doctor=doctor,
                    notes=notes
                )

def verify_database():
    """Verify database initialization by printing all appointments"""
    db = DatabaseManager()
    appointments = db.get_appointments()
    
    print("\nCurrent Appointments in Database:")
    print("-" * 80)
    for apt in appointments:
        print(f"Date: {apt['date']}, Time: {apt['time']}, Doctor: {apt['doctor']}")
        print(f"Notes: {apt['patient_notes']}")
        print(f"Status: {apt['status']}")
        print("-" * 80)

if __name__ == "__main__":
    print("Initializing database...")
    initialize_database()
    verify_database()
    print("\nDatabase initialization complete!")