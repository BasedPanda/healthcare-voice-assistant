"""
Healthcare Voice Assistant
A voice-enabled system for scheduling and managing healthcare appointments.

This package provides a complete system for:
- Voice command processing
- Natural language understanding
- Appointment scheduling
- Speech synthesis
"""

from .speech.speech_handler import SpeechHandler
from .nlp.intent_processor import IntentProcessor
from .scheduling.appointment import AppointmentManager
from .database.db_manager import DatabaseManager

# Package metadata
__version__ = '1.0.0'
__author__ = 'Your Name'
__email__ = 'your.email@example.com'
__description__ = 'Voice-enabled healthcare appointment scheduling system'

# Version information tuple
VERSION_INFO = (1, 0, 0)

# Define what gets imported with 'from src import *'
__all__ = [
    'SpeechHandler',
    'IntentProcessor',
    'AppointmentManager',
    'DatabaseManager',
    'create_assistant',
    'get_version',
]

def create_assistant(config=None):
    """
    Factory function to create a fully configured healthcare voice assistant.
    
    Args:
        config (dict, optional): Configuration dictionary for customizing the assistant
        
    Returns:
        tuple: Initialized instances of (SpeechHandler, IntentProcessor, AppointmentManager, DatabaseManager)
    """
    try:
        # Initialize components with provided config or defaults
        speech_handler = SpeechHandler(config.get('speech', {}) if config else None)
        intent_processor = IntentProcessor()
        appointment_manager = AppointmentManager()
        database_manager = DatabaseManager()
        
        return speech_handler, intent_processor, appointment_manager, database_manager
        
    except Exception as e:
        raise RuntimeError(f"Failed to initialize healthcare assistant: {e}")

def get_version():
    """
    Get the current version of the package.
    
    Returns:
        str: Version string
    """
    return __version__

# Runtime initialization and checks
def _check_dependencies():
    """Verify that all required dependencies are available"""
    required_packages = {
        'speech_recognition': 'speech_recognition',
        'pyttsx3': 'pyttsx3',
        'spacy': 'spacy',
        'python-dateutil': 'dateutil'
    }
    
    missing_packages = []
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        raise ImportError(
            f"Missing required packages: {', '.join(missing_packages)}. "
            f"Please install them using: pip install {' '.join(missing_packages)}"
        )

# Configuration validation
def _validate_config(config):
    """
    Validate configuration dictionary
    
    Args:
        config (dict): Configuration to validate
        
    Returns:
        dict: Validated configuration with defaults applied
    """
    default_config = {
        'speech': {
            'speech_rate': 150,
            'speech_volume': 0.9,
            'voice_gender': 'female',
            'timeout': 5,
            'phrase_timeout': 3,
            'energy_threshold': 4000,
            'dynamic_energy_threshold': True,
            'wake_words': ['assistant', 'hey assistant', 'hello assistant']
        },
        'database': {
            'path': 'data/appointments.db'
        },
        'scheduling': {
            'working_hours_start': 9,
            'working_hours_end': 17,
            'appointment_duration': 30,
            'min_schedule_notice': 1
        }
    }
    
    if config is None:
        return default_config
        
    # Deep merge config with defaults
    merged_config = default_config.copy()
    for key, value in config.items():
        if isinstance(value, dict) and key in merged_config:
            merged_config[key].update(value)
        else:
            merged_config[key] = value
            
    return merged_config

# Utility functions for package users
def get_sample_config():
    """
    Get a sample configuration dictionary with all available options
    
    Returns:
        dict: Sample configuration
    """
    return {
        'speech': {
            'speech_rate': 150,  # Words per minute
            'speech_volume': 0.9,  # Volume level (0.0 to 1.0)
            'voice_gender': 'female',  # 'male' or 'female'
            'timeout': 5,  # Seconds to wait for speech
            'phrase_timeout': 3,  # Seconds to wait for phrase completion
            'energy_threshold': 4000,  # Minimum audio energy to detect
            'dynamic_energy_threshold': True,  # Automatically adjust energy threshold
            'wake_words': ['assistant', 'hey assistant', 'hello assistant']  # Wake words to activate assistant
        },
        'database': {
            'path': 'data/appointments.db'  # Path to SQLite database file
        },
        'scheduling': {
            'working_hours_start': 9,  # Start of working hours (24-hour format)
            'working_hours_end': 17,  # End of working hours (24-hour format)
            'appointment_duration': 30,  # Minutes per appointment
            'min_schedule_notice': 1  # Minimum hours notice required for scheduling
        }
    }

# Run dependency checks at import time
_check_dependencies()