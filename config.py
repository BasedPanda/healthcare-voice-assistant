import os
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Configuration class for the Healthcare Voice Assistant"""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """
        Get the complete configuration dictionary
        
        Returns:
            Dict containing all configuration settings
        """
        return {
            'app': {
                'debug': _get_bool('DEBUG', False),
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'environment': os.getenv('ENVIRONMENT', 'development')
            },
            'speech': {
                'speech_rate': _get_int('SPEECH_RATE', 150),
                'speech_volume': _get_float('SPEECH_VOLUME', 0.9),
                'voice_gender': os.getenv('VOICE_GENDER', 'female'),
                'timeout': _get_int('SPEECH_TIMEOUT', 5),
                'energy_threshold': _get_int('ENERGY_THRESHOLD', 4000),
                'wake_words': _get_list('WAKE_WORDS', ['assistant', 'hey assistant', 'hello assistant'])
            },
            'database': {
                'path': os.getenv('DATABASE_PATH', str(BASE_DIR / 'data' / 'appointments.db'))
            },
            'scheduling': {
                'working_hours_start': _get_int('WORKING_HOURS_START', 9),
                'working_hours_end': _get_int('WORKING_HOURS_END', 17),
                'appointment_duration': _get_int('APPOINTMENT_DURATION', 30),
                'min_schedule_notice': _get_int('MIN_SCHEDULE_NOTICE', 1)
            },
            'logging': {
                'log_file_path': os.getenv('LOG_FILE_PATH', str(BASE_DIR / 'logs' / 'healthcare_assistant.log'))
            }
        }
    
    @staticmethod
    def get_speech_config() -> Dict[str, Any]:
        """Get speech-specific configuration"""
        return Config.get_config()['speech']
    
    @staticmethod
    def get_database_config() -> Dict[str, Any]:
        """Get database-specific configuration"""
        return Config.get_config()['database']
    
    @staticmethod
    def get_scheduling_config() -> Dict[str, Any]:
        """Get scheduling-specific configuration"""
        return Config.get_config()['scheduling']
    
    @staticmethod
    def get_logging_config() -> Dict[str, Any]:
        """Get logging-specific configuration"""
        return Config.get_config()['logging']

def _get_bool(key: str, default: bool = False) -> bool:
    """Convert environment variable to boolean"""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 't', 'y', 'yes')

def _get_int(key: str, default: int) -> int:
    """Convert environment variable to integer"""
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default

def _get_float(key: str, default: float) -> float:
    """Convert environment variable to float"""
    try:
        return float(os.getenv(key, default))
    except (TypeError, ValueError):
        return default

def _get_list(key: str, default: List) -> List:
    """Convert comma-separated environment variable to list"""
    value = os.getenv(key)
    if value:
        return [item.strip() for item in value.split(',')]
    return default

# Create required directories
def init_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        BASE_DIR / 'data',
        BASE_DIR / 'logs',
        BASE_DIR / 'audio'
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)

# Initialize directories when config is imported
init_directories()

# Export configuration
config = Config.get_config()