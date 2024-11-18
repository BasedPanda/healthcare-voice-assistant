from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional, Tuple
from ..database.db_manager import DatabaseManager

class AppointmentManager:
    def __init__(self):
        """Initialize appointment manager with database connection"""
        self.db = DatabaseManager()
        
        # Configuration for appointments
        self.WORKING_HOURS_START = 9  # 9 AM
        self.WORKING_HOURS_END = 17   # 5 PM
        self.APPOINTMENT_DURATION = 30 # minutes
        self.MIN_SCHEDULE_NOTICE = 1   # hours
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def schedule_appointment(self, date: str, time: str, doctor: str, notes: str = "") -> Tuple[bool, str]:
        """
        Schedule a new appointment
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            doctor: Doctor's name or specialty
            notes: Optional appointment notes
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate date and time
            if not self._is_valid_datetime(date, time):
                return False, "Invalid appointment date or time"
                
            # Check if slot is available
            if not self.is_available(date, time):
                return False, "This time slot is not available"
                
            # Add appointment to database
            success = self.db.add_appointment(date, time, doctor, notes)
            
            if success:
                return True, "Appointment scheduled successfully"
            else:
                return False, "Failed to schedule appointment"
                
        except Exception as e:
            self.logger.error(f"Error scheduling appointment: {e}")
            return False, "An error occurred while scheduling the appointment"

    def cancel_appointment(self, date: str, time: str) -> Tuple[bool, str]:
        """
        Cancel an existing appointment
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            success = self.db.cancel_appointment(date, time)
            
            if success:
                return True, "Appointment cancelled successfully"
            else:
                return False, "No appointment found for the specified time"
                
        except Exception as e:
            self.logger.error(f"Error cancelling appointment: {e}")
            return False, "An error occurred while cancelling the appointment"

    def get_appointments(self, date: Optional[str] = None) -> List[Dict]:
        """
        Retrieve appointments, optionally filtered by date
        
        Args:
            date: Optional date filter in YYYY-MM-DD format
            
        Returns:
            List of appointment dictionaries
        """
        try:
            appointments = self.db.get_appointments(date)
            return appointments
            
        except Exception as e:
            self.logger.error(f"Error retrieving appointments: {e}")
            return []

    def is_available(self, date: str, time: str) -> bool:
        """
        Check if a time slot is available
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            
        Returns:
            bool: True if slot is available
        """
        try:
            # First check if it's within working hours and not in the past
            if not self._is_valid_datetime(date, time):
                return False
                
            # Then check database for existing appointments
            return self.db.check_availability(date, time)
            
        except Exception as e:
            self.logger.error(f"Error checking availability: {e}")
            return False

    def get_next_available_slot(self, date: str = None) -> Optional[Dict[str, str]]:
        """
        Find the next available appointment slot
        
        Args:
            date: Optional starting date in YYYY-MM-DD format
            
        Returns:
            Dictionary with date and time if found, None otherwise
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
                
            current_date = datetime.strptime(date, '%Y-%m-%d')
            
            # Look for slots in the next 30 days
            for _ in range(30):
                date_str = current_date.strftime('%Y-%m-%d')
                
                # Check each time slot during working hours
                current_time = datetime.strptime(f"{self.WORKING_HOURS_START}:00", '%H:%M')
                end_time = datetime.strptime(f"{self.WORKING_HOURS_END}:00", '%H:%M')
                
                while current_time < end_time:
                    time_str = current_time.strftime('%H:%M')
                    
                    if self.is_available(date_str, time_str):
                        return {
                            'date': date_str,
                            'time': time_str
                        }
                    
                    # Move to next slot
                    current_time += timedelta(minutes=self.APPOINTMENT_DURATION)
                
                # Move to next day
                current_date += timedelta(days=1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding next available slot: {e}")
            return None

    def get_daily_schedule(self, date: str) -> List[Dict]:
        """
        Get complete schedule for a specific day
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            List of appointments for the day
        """
        try:
            return self.db.get_appointments(date)
        except Exception as e:
            self.logger.error(f"Error retrieving daily schedule: {e}")
            return []

    def update_appointment_notes(self, date: str, time: str, notes: str) -> Tuple[bool, str]:
        """
        Update notes for an existing appointment
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            notes: New notes to add
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            success = self.db.update_appointment_notes(date, time, notes)
            
            if success:
                return True, "Appointment notes updated successfully"
            else:
                return False, "No appointment found for the specified time"
                
        except Exception as e:
            self.logger.error(f"Error updating appointment notes: {e}")
            return False, "An error occurred while updating the notes"

    def _is_valid_datetime(self, date: str, time: str) -> bool:
        """
        Validate if the date and time are valid for scheduling
        
        Args:
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            
        Returns:
            bool: True if date and time are valid
        """
        try:
            # Parse date and time
            dt_str = f"{date} {time}"
            appointment_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            
            # Get current time
            now = datetime.now()
            
            # Check if appointment is in the past
            if appointment_dt < now + timedelta(hours=self.MIN_SCHEDULE_NOTICE):
                return False
                
            # Check if it's within working hours
            hour = appointment_dt.hour
            if hour < self.WORKING_HOURS_START or hour >= self.WORKING_HOURS_END:
                return False
                
            # Check if it's on a weekend
            if appointment_dt.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                return False
                
            return True
            
        except ValueError:
            return False

    def suggest_alternative_slots(self, date: str, time: str, num_suggestions: int = 3) -> List[Dict[str, str]]:
        """
        Suggest alternative time slots if requested slot is unavailable
        
        Args:
            date: Preferred date in YYYY-MM-DD format
            time: Preferred time in HH:MM format
            num_suggestions: Number of alternatives to suggest
            
        Returns:
            List of dictionaries with alternative dates and times
        """
        suggestions = []
        try:
            preferred_dt = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
            current_dt = preferred_dt
            
            while len(suggestions) < num_suggestions and len(suggestions) < 10:
                # Try next available slot
                current_dt += timedelta(minutes=self.APPOINTMENT_DURATION)
                
                # Reset to next day if we've passed working hours
                if current_dt.hour >= self.WORKING_HOURS_END:
                    current_dt = datetime.combine(
                        current_dt.date() + timedelta(days=1),
                        datetime.strptime(f"{self.WORKING_HOURS_START}:00", '%H:%M').time()
                    )
                
                # Skip weekends
                while current_dt.weekday() >= 5:
                    current_dt += timedelta(days=1)
                    current_dt = datetime.combine(
                        current_dt.date(),
                        datetime.strptime(f"{self.WORKING_HOURS_START}:00", '%H:%M').time()
                    )
                
                current_date = current_dt.strftime('%Y-%m-%d')
                current_time = current_dt.strftime('%H:%M')
                
                if self.is_available(current_date, current_time):
                    suggestions.append({
                        'date': current_date,
                        'time': current_time
                    })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error suggesting alternative slots: {e}")
            return []