import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

class DatabaseManager:
    def __init__(self, db_path: str = "data/appointments.db"):
        """
        Initialize database manager with the specified database path
        """
        self.db_path = db_path
        self._ensure_database_directory()
        self._init_database()
        
    def _ensure_database_directory(self):
        """Ensure the directory for the database file exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def _init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create appointments table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS appointments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        doctor TEXT NOT NULL,
                        patient_notes TEXT,
                        status TEXT DEFAULT 'scheduled',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            raise

    def add_appointment(self, date: str, time: str, doctor: str, notes: str = "") -> bool:
        """
        Add a new appointment to the database
        
        Args:
            date: Appointment date (YYYY-MM-DD)
            time: Appointment time (HH:MM)
            doctor: Doctor's name or specialty
            notes: Optional patient notes
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO appointments (date, time, doctor, patient_notes)
                    VALUES (?, ?, ?, ?)
                ''', (date, time, doctor, notes))
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logging.error(f"Error adding appointment: {e}")
            return False

    def get_appointments(self, date: Optional[str] = None) -> List[Dict]:
        """
        Retrieve appointments, optionally filtered by date
        
        Args:
            date: Optional date filter (YYYY-MM-DD)
            
        Returns:
            List of appointment dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if date:
                    cursor.execute('''
                        SELECT * FROM appointments 
                        WHERE date = ? AND status = 'scheduled'
                        ORDER BY time
                    ''', (date,))
                else:
                    cursor.execute('''
                        SELECT * FROM appointments 
                        WHERE date >= date('now') 
                        AND status = 'scheduled'
                        ORDER BY date, time
                    ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logging.error(f"Error retrieving appointments: {e}")
            return []

    def cancel_appointment(self, date: str, time: str) -> bool:
        """
        Cancel an appointment by updating its status
        
        Args:
            date: Appointment date (YYYY-MM-DD)
            time: Appointment time (HH:MM)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE appointments 
                    SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
                    WHERE date = ? AND time = ? AND status = 'scheduled'
                ''', (date, time))
                
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            logging.error(f"Error cancelling appointment: {e}")
            return False

    def check_availability(self, date: str, time: str) -> bool:
        """
        Check if a given time slot is available
        
        Args:
            date: Date to check (YYYY-MM-DD)
            time: Time to check (HH:MM)
            
        Returns:
            bool: True if available, False if slot is taken
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM appointments
                    WHERE date = ? AND time = ? AND status = 'scheduled'
                ''', (date, time))
                
                count = cursor.fetchone()[0]
                return count == 0
                
        except sqlite3.Error as e:
            logging.error(f"Error checking availability: {e}")
            return False

    def update_appointment_notes(self, date: str, time: str, notes: str) -> bool:
        """
        Update notes for an existing appointment
        
        Args:
            date: Appointment date (YYYY-MM-DD)
            time: Appointment time (HH:MM)
            notes: New notes to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE appointments 
                    SET patient_notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE date = ? AND time = ? AND status = 'scheduled'
                ''', (notes, date, time))
                
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            logging.error(f"Error updating appointment notes: {e}")
            return False