"""
Centralized Input Validation and Error Handling Module (UC6)
=============================================================

Single source of truth for all validation logic across the system.
KISS principle: Keep It Simple, Stupid.
"""

from decimal import Decimal, InvalidOperation
from core.exceptions import ValidationException
from core.logger import logger
import re


class InputValidator:
    """Centralized validation functions for all input validation needs"""
    
    # ===== NUMERIC INPUT PARSING =====
    
    @staticmethod
    def parse_float_safe(value: str, field_name: str = "value") -> float:
        """
        Safely parse string to float. Handles None, empty, and invalid inputs.
        
        Args:
            value: String value to parse
            field_name: Name of field for error message
            
        Returns:
            float: Parsed value
            
        Raises:
            ValidationException: If value is invalid
        """
        if value is None or value == "":
            raise ValidationException(f"{field_name} cannot be empty")
        
        try:
            result = float(value)
            return result
        except (ValueError, TypeError):
            raise ValidationException(f"{field_name} must be a valid number, got '{value}'")
    
    @staticmethod
    def parse_decimal_safe(value, field_name: str = "value") -> Decimal:
        """
        Safely parse to Decimal. Handles strings and float inputs.
        
        Args:
            value: Value to parse (str or Decimal or float)
            field_name: Name of field for error message
            
        Returns:
            Decimal: Parsed value
            
        Raises:
            ValidationException: If value is invalid
        """
        if value is None or value == "":
            raise ValidationException(f"{field_name} cannot be empty")
        
        try:
            if isinstance(value, Decimal):
                return value
            # Convert to string first to avoid float precision issues
            return Decimal(str(value))
        except (ValueError, TypeError, InvalidOperation):
            raise ValidationException(f"{field_name} must be a valid number, got '{value}'")
    
    @staticmethod
    def parse_int_safe(value: str, field_name: str = "value") -> int:
        """
        Safely parse string to integer.
        
        Args:
            value: String value to parse
            field_name: Name of field for error message
            
        Returns:
            int: Parsed value
            
        Raises:
            ValidationException: If value is invalid
        """
        if value is None or value == "":
            raise ValidationException(f"{field_name} cannot be empty")
        
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationException(f"{field_name} must be a valid integer, got '{value}'")
    
    # ===== STAKE VALIDATION =====
    
    @staticmethod
    def validate_stake(stake_value, field_name: str = "stake") -> Decimal:
        """
        Validate stake amount.
        
        Requirements:
        - Must be > 0
        - Must not be None
        - Must be numeric
        
        Args:
            stake_value: Stake value (str, Decimal, or float)
            field_name: Name of field for error message
            
        Returns:
            Decimal: Validated stake
            
        Raises:
            ValidationException: If validation fails
        """
        stake = InputValidator.parse_decimal_safe(stake_value, field_name)
        
        if stake <= 0:
            raise ValidationException(f"{field_name} must be greater than 0, got {stake}")
        
        logger.info(f"✓ {field_name} validated: ${stake}")
        return stake
    
    @staticmethod
    def validate_initial_stake(stake_value) -> Decimal:
        """Validate initial stake specifically"""
        return InputValidator.validate_stake(stake_value, "initial_stake")
    
    # ===== BET AMOUNT VALIDATION =====
    
    @staticmethod
    def validate_bet_amount(bet_amount, current_stake: Decimal, 
                           field_name: str = "bet_amount") -> Decimal:
        """
        Validate bet amount.
        
        Requirements:
        - Must be > 0
        - Must be ≤ current stake
        
        Args:
            bet_amount: Bet amount (str, Decimal, or float)
            current_stake: Current stake balance
            field_name: Name of field for error message
            
        Returns:
            Decimal: Validated bet amount
            
        Raises:
            ValidationException: If validation fails
        """
        bet = InputValidator.parse_decimal_safe(bet_amount, field_name)
        
        if bet <= 0:
            raise ValidationException(f"{field_name} must be greater than 0, got {bet}")
        
        if bet > current_stake:
            raise ValidationException(
                f"Insufficient stake: {field_name} is ${bet} but current stake is only ${current_stake}"
            )
        
        logger.info(f"✓ {field_name} validated: ${bet}")
        return bet
    
    # ===== LIMITS VALIDATION =====
    
    @staticmethod
    def validate_limits(initial_stake: Decimal, win_threshold: Decimal, 
                       loss_threshold: Decimal) -> tuple:
        """
        Validate thresholds.
        
        Requirements:
        - win_threshold > initial_stake
        - loss_threshold < initial_stake
        
        Args:
            initial_stake: Initial stake amount
            win_threshold: Win threshold amount
            loss_threshold: Loss threshold amount
            
        Returns:
            tuple: (initial_stake, win_threshold, loss_threshold)
            
        Raises:
            ValidationException: If validation fails
        """
        initial = InputValidator.validate_stake(initial_stake, "initial_stake")
        win = InputValidator.parse_decimal_safe(win_threshold, "win_threshold")
        loss = InputValidator.parse_decimal_safe(loss_threshold, "loss_threshold")
        
        errors = []
        
        if win <= initial:
            errors.append(f"win_threshold (${win}) must be greater than initial_stake (${initial})")
        
        if loss >= initial:
            errors.append(f"loss_threshold (${loss}) must be less than initial_stake (${initial})")
        
        if loss < 0:
            errors.append(f"loss_threshold cannot be negative")
        
        if errors:
            raise ValidationException("; ".join(errors))
        
        logger.info(f"✓ Limits validated: loss=${loss} < initial=${initial} < win=${win}")
        return initial, win, loss
    
    # ===== PROBABILITY VALIDATION =====
    
    @staticmethod
    def validate_probability(probability_value, field_name: str = "probability") -> float:
        """
        Validate probability.
        
        Requirements:
        - 0 ≤ probability ≤ 1
        
        Args:
            probability_value: Probability value (str or float)
            field_name: Name of field for error message
            
        Returns:
            float: Validated probability
            
        Raises:
            ValidationException: If validation fails
        """
        prob = InputValidator.parse_float_safe(probability_value, field_name)
        
        if not (0.0 <= prob <= 1.0):
            raise ValidationException(
                f"{field_name} must be between 0.0 and 1.0, got {prob}"
            )
        
        logger.info(f"✓ {field_name} validated: {prob:.1%}")
        return prob
    
    # ===== GENERIC VALIDATORS =====
    
    @staticmethod
    def validate_positive(value, field_name: str = "value") -> Decimal:
        """
        Validate that a value is positive (> 0).
        
        Args:
            value: Value to validate
            field_name: Name of field for error message
            
        Returns:
            Decimal: Validated value
            
        Raises:
            ValidationException: If value is not positive
        """
        val = InputValidator.parse_decimal_safe(value, field_name)
        
        if val <= 0:
            raise ValidationException(f"{field_name} must be greater than 0, got {val}")
        
        return val
    
    @staticmethod
    def validate_non_negative(value, field_name: str = "value") -> Decimal:
        """
        Validate that a value is non-negative (≥ 0).
        
        Args:
            value: Value to validate
            field_name: Name of field for error message
            
        Returns:
            Decimal: Validated value
            
        Raises:
            ValidationException: If value is negative
        """
        val = InputValidator.parse_decimal_safe(value, field_name)
        
        if val < 0:
            raise ValidationException(f"{field_name} cannot be negative, got {val}")
        
        return val
    
    @staticmethod
    def validate_in_range(value_str: str, min_val: float, max_val: float, 
                         field_name: str = "value") -> float:
        """
        Validate that parsed value is within a range.
        
        Args:
            value_str: String value to parse
            min_val: Minimum allowed value (inclusive)
            max_val: Maximum allowed value (inclusive)
            field_name: Name of field for error message
            
        Returns:
            float: Validated value
            
        Raises:
            ValidationException: If value is out of range
        """
        val = InputValidator.parse_float_safe(value_str, field_name)
        
        if not (min_val <= val <= max_val):
            raise ValidationException(
                f"{field_name} must be between {min_val} and {max_val}, got {val}"
            )
        
        return val
    
    # ===== STRING VALIDATION =====
    
    @staticmethod
    def validate_non_empty_string(value: str, field_name: str = "string", 
                                 max_length: int = None) -> str:
        """
        Validate that string is not empty.
        
        Args:
            value: String value to validate
            field_name: Name of field for error message
            max_length: Maximum allowed length (optional)
            
        Returns:
            str: Validated string
            
        Raises:
            ValidationException: If validation fails
        """
        if value is None or value == "" or not value.strip():
            raise ValidationException(f"{field_name} cannot be empty")
        
        cleaned = value.strip()
        
        if max_length and len(cleaned) > max_length:
            raise ValidationException(
                f"{field_name} exceeds maximum length of {max_length} characters"
            )
        
        return cleaned
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            str: Validated email
            
        Raises:
            ValidationException: If email is invalid
        """
        email = InputValidator.validate_non_empty_string(email, "email")
        
        # Simple email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            raise ValidationException(f"Invalid email format: {email}")
        
        return email
    
    # ===== ID VALIDATION =====
    
    @staticmethod
    def validate_positive_integer(value_str: str, field_name: str = "ID") -> int:
        """
        Validate that parsed integer is positive.
        
        Args:
            value_str: String value to parse
            field_name: Name of field for error message
            
        Returns:
            int: Validated positive integer
            
        Raises:
            ValidationException: If value is invalid or not positive
        """
        val = InputValidator.parse_int_safe(value_str, field_name)
        
        if val <= 0:
            raise ValidationException(f"{field_name} must be a positive integer, got {val}")
        
        return val
    
    # ===== HELPER: GAMBLER CREATION VALIDATION =====
    
    @staticmethod
    def validate_gambler_creation(username: str, full_name: str, email: str,
                                 initial_stake, win_threshold, 
                                 loss_threshold, min_bet_amount):
        """
        Validate all inputs for gambler creation.
        
        Args:
            username: Username
            full_name: Full name
            email: Email address
            initial_stake: Initial stake amount
            win_threshold: Win threshold amount
            loss_threshold: Loss threshold amount
            min_bet_amount: Minimum bet amount
            
        Returns:
            dict: Validated inputs
            
        Raises:
            ValidationException: If any validation fails
        """
        errors = []
        
        # Validate username
        try:
            username_clean = InputValidator.validate_non_empty_string(username, "username", 50)
        except ValidationException as e:
            errors.append(str(e))
            username_clean = None
        
        # Validate full_name
        try:
            fullname_clean = InputValidator.validate_non_empty_string(full_name, "full_name", 100)
        except ValidationException as e:
            errors.append(str(e))
            fullname_clean = None
        
        # Validate email
        try:
            email_clean = InputValidator.validate_email(email)
        except ValidationException as e:
            errors.append(str(e))
            email_clean = None
        
        # Validate initial stake
        try:
            initial_clean = InputValidator.validate_initial_stake(initial_stake)
        except ValidationException as e:
            errors.append(str(e))
            initial_clean = None
        
        # Validate thresholds
        try:
            win_clean = InputValidator.parse_decimal_safe(win_threshold, "win_threshold")
            loss_clean = InputValidator.parse_decimal_safe(loss_threshold, "loss_threshold")
            
            if initial_clean:
                if win_clean <= initial_clean:
                    errors.append(f"win_threshold (${win_clean}) must be > initial_stake (${initial_clean})")
                if loss_clean >= initial_clean:
                    errors.append(f"loss_threshold (${loss_clean}) must be < initial_stake (${initial_clean})")
                if loss_clean < 0:
                    errors.append("loss_threshold cannot be negative")
        except ValidationException as e:
            errors.append(str(e))
            win_clean = None
            loss_clean = None
        
        # Validate min bet
        try:
            min_clean = InputValidator.validate_non_negative(min_bet_amount, "min_bet_amount")
        except ValidationException as e:
            errors.append(str(e))
            min_clean = None
        
        if errors:
            raise ValidationException("; ".join(errors))
        
        return {
            'username': username_clean,
            'full_name': fullname_clean,
            'email': email_clean,
            'initial_stake': initial_clean,
            'win_threshold': win_clean,
            'loss_threshold': loss_clean,
            'min_bet_amount': min_clean
        }
