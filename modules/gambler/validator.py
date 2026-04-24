"""Gambler-specific validation - uses centralized InputValidator"""

from decimal import Decimal
from core.exceptions import ValidationException
from modules.validation import InputValidator
import re


class GamblerValidator:
    """Gambler validation using centralized InputValidator"""
    
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
        
        # Validate email format using centralized validator
        try:
            InputValidator.validate_email(data.email)
        except ValidationException as e:
            errors.append(str(e))
        
        # Validate initial_stake using centralized validator
        try:
            InputValidator.validate_initial_stake(data.initial_stake)
        except ValidationException as e:
            errors.append(str(e))
        
        # Validate thresholds using centralized validator
        try:
            InputValidator.validate_limits(
                data.initial_stake, 
                data.win_threshold, 
                data.loss_threshold
            )
        except ValidationException as e:
            errors.append(str(e))
        
        # Validate min_required_stake
        if data.min_required_stake < 0:
            errors.append("min_required_stake cannot be negative")
        
        if errors:
            raise ValidationException("; ".join(errors))
    
    @staticmethod
    def validate_eligibility(current_stake: Decimal, min_required_stake: Decimal) -> bool:
        """Check if gambler's current stake meets minimum requirement"""
        return current_stake >= min_required_stake


