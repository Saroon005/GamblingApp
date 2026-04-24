from decimal import Decimal
from core.exceptions import ValidationException


class BettingValidator:
    
    @staticmethod
    def validate_place_bet(gambler_id: int, bet_amount: Decimal, win_probability: float, 
                          current_stake: Decimal):
        """Validate bet placement parameters"""
        errors = []
        
        if gambler_id <= 0:
            errors.append("gambler_id must be a positive integer")
        
        if bet_amount <= 0:
            errors.append("bet_amount must be greater than 0")
        
        if current_stake < bet_amount:
            errors.append(f"insufficient stake: have ${current_stake}, need ${bet_amount}")
        
        if not (0.0 <= win_probability <= 1.0):
            errors.append("win_probability must be between 0.0 and 1.0")
        
        if errors:
            raise ValidationException("; ".join(errors))
    
    @staticmethod
    def validate_bet_strategy(strategy_type: str, strategy_value: Decimal, current_stake: Decimal):
        """Validate betting strategy parameters"""
        errors = []
        
        if strategy_type.upper() not in ["FIXED", "PERCENTAGE"]:
            errors.append("strategy_type must be 'FIXED' or 'PERCENTAGE'")
        
        if strategy_value <= 0:
            errors.append("strategy_value must be greater than 0")
        
        if strategy_type.upper() == "PERCENTAGE":
            if strategy_value > 100:
                errors.append("percentage strategy value cannot exceed 100")
        elif strategy_type.upper() == "FIXED":
            if strategy_value > current_stake:
                errors.append(f"fixed bet amount ${strategy_value} exceeds current stake ${current_stake}")
        
        if errors:
            raise ValidationException("; ".join(errors))
    
    @staticmethod
    def validate_win_probability(probability: float):
        """Validate win probability"""
        if not isinstance(probability, (int, float)):
            raise ValidationException("win_probability must be a number")
        
        if not (0.0 <= probability <= 1.0):
            raise ValidationException("win_probability must be between 0.0 and 1.0")
    
    @staticmethod
    def validate_game_index(game_index: int):
        """Validate game index"""
        if game_index <= 0:
            raise ValidationException("game_index must be a positive integer")
