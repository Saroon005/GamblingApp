from decimal import Decimal
from core.exceptions import ValidationException
import re


class GamblerValidator:
    @staticmethod
    def validate_creation_data(data):
        """Validate gambler creation data"""
        errors = []
        
        # Validate username
        if not data.username or len(data.username) < 1 or len(data.username) > 50:
            errors.append("username must be between 1 and 50 characters")
        
        # Validate full_name
        if not data.full_name or len(data.full_name) < 1 or len(data.full_name) > 100:
            errors.append("full_name must be between 1 and 100 characters")
        
        # Validate email format
        if not data.email or not GamblerValidator._is_valid_email(data.email):
            errors.append("email must be a valid email address")
        
        # Validate initial_stake
        if data.initial_stake <= 0:
            errors.append("initial_stake must be greater than 0")
        
        # Validate win_threshold
        if data.win_threshold <= data.initial_stake:
            errors.append("win_threshold must be greater than initial_stake")
        
        # Validate loss_threshold
        if data.loss_threshold >= data.initial_stake:
            errors.append("loss_threshold must be less than initial_stake")
        
        # Validate min_required_stake
        if data.min_required_stake < 0:
            errors.append("min_required_stake cannot be negative")
        
        if errors:
            raise ValidationException("; ".join(errors))
    
    @staticmethod
    def _is_valid_email(email):
        """Simple email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_eligibility(current_stake: Decimal, min_required_stake: Decimal) -> bool:
        """Check if gambler's current stake meets minimum requirement"""
        return current_stake >= min_required_stake

