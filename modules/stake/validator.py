from decimal import Decimal
from core.exceptions import ValidationException


class StakeValidator:
    
    TRANSACTION_TYPES = {
        "INITIAL_STAKE", "BET_WIN", "BET_LOSS", 
        "DEPOSIT", "WITHDRAWAL", "RESET"
    }
    
    @staticmethod
    def validate_initialization(gambler_id: int, initial_balance: Decimal):
        """Validate stake initialization parameters"""
        errors = []
        
        if gambler_id <= 0:
            errors.append("gambler_id must be a positive integer")
        
        if initial_balance <= 0:
            errors.append("initial_balance must be greater than 0")
        
        if errors:
            raise ValidationException("; ".join(errors))
    
    @staticmethod
    def validate_bet_outcome(gambler_id: int, bet_amount: Decimal, is_win: bool, current_balance: Decimal):
        """Validate bet outcome parameters"""
        errors = []
        
        if gambler_id <= 0:
            errors.append("gambler_id must be a positive integer")
        
        if bet_amount <= 0:
            errors.append("bet_amount must be greater than 0")
        
        if not isinstance(is_win, bool):
            errors.append("is_win must be a boolean")
        
        # Check if balance won't go below zero after loss
        if not is_win and current_balance < bet_amount:
            errors.append("insufficient balance for this bet loss")
        
        if errors:
            raise ValidationException("; ".join(errors))
    
    @staticmethod
    def validate_deposit(gambler_id: int, amount: Decimal):
        """Validate deposit parameters"""
        errors = []
        
        if gambler_id <= 0:
            errors.append("gambler_id must be a positive integer")
        
        if amount <= 0:
            errors.append("deposit amount must be greater than 0")
        
        if errors:
            raise ValidationException("; ".join(errors))
    
    @staticmethod
    def validate_withdrawal(gambler_id: int, amount: Decimal, current_balance: Decimal):
        """Validate withdrawal parameters"""
        errors = []
        
        if gambler_id <= 0:
            errors.append("gambler_id must be a positive integer")
        
        if amount <= 0:
            errors.append("withdrawal amount must be greater than 0")
        
        if current_balance < amount:
            errors.append("insufficient balance for withdrawal")
        
        if errors:
            raise ValidationException("; ".join(errors))
    
    @staticmethod
    def validate_stake_boundary(balance: Decimal, lower_limit: Decimal = None, upper_limit: Decimal = None):
        """Validate stake is within boundaries"""
        errors = []
        
        if balance < Decimal("0"):
            errors.append("stake balance cannot be negative")
        
        if lower_limit is not None and balance < lower_limit:
            errors.append(f"stake balance {balance} is below lower limit {lower_limit}")
        
        if upper_limit is not None and balance > upper_limit:
            errors.append(f"stake balance {balance} exceeds upper limit {upper_limit}")
        
        if errors:
            raise ValidationException("; ".join(errors))
    
    @staticmethod
    def validate_transaction_type(transaction_type: str):
        """Validate transaction type"""
        if transaction_type not in StakeValidator.TRANSACTION_TYPES:
            raise ValidationException(
                f"Invalid transaction_type: {transaction_type}. "
                f"Allowed types: {', '.join(StakeValidator.TRANSACTION_TYPES)}"
            )
    
    @staticmethod
    def validate_gambler_id(gambler_id: int):
        """Validate gambler_id is positive"""
        if gambler_id <= 0:
            raise ValidationException("gambler_id must be a positive integer")
