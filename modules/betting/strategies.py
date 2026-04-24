from decimal import Decimal
from core.logger import logger
from core.exceptions import ValidationException


class BettingStrategy:
    """Base class for betting strategies"""
    
    def calculate_bet_amount(self, current_stake: Decimal) -> Decimal:
        """Calculate bet amount based on strategy"""
        raise NotImplementedError


class FixedStrategy(BettingStrategy):
    """Fixed amount betting strategy"""
    
    def __init__(self, fixed_amount: Decimal):
        self.fixed_amount = Decimal(str(fixed_amount))
        logger.debug(f"FixedStrategy initialized with amount: ${self.fixed_amount}")
    
    def calculate_bet_amount(self, current_stake: Decimal) -> Decimal:
        """Return the fixed bet amount"""
        if current_stake < self.fixed_amount:
            logger.warning(f"Fixed bet amount ${self.fixed_amount} exceeds current stake ${current_stake}")
            return current_stake  # Bet all remaining stake
        
        logger.debug(f"FixedStrategy: betting ${self.fixed_amount}")
        return self.fixed_amount


class PercentageStrategy(BettingStrategy):
    """Percentage-based betting strategy"""
    
    def __init__(self, percentage: Decimal):
        self.percentage = Decimal(str(percentage))
        
        if self.percentage <= 0 or self.percentage > 100:
            raise ValidationException("percentage must be between 0 and 100")
        
        logger.debug(f"PercentageStrategy initialized with {self.percentage}% of stake")
    
    def calculate_bet_amount(self, current_stake: Decimal) -> Decimal:
        """Calculate bet amount as percentage of current stake"""
        bet_amount = (current_stake * self.percentage) / Decimal("100")
        bet_amount = bet_amount.quantize(Decimal("0.01"))  # Round to 2 decimals
        
        logger.debug(f"PercentageStrategy: betting {self.percentage}% = ${bet_amount} (stake: ${current_stake})")
        return bet_amount


class StrategyFactory:
    """Factory for creating betting strategies"""
    
    @staticmethod
    def create_strategy(strategy_type: str, strategy_value: Decimal) -> BettingStrategy:
        """Create strategy based on type and value"""
        strategy_type = strategy_type.upper()
        
        if strategy_type == "FIXED":
            return FixedStrategy(strategy_value)
        elif strategy_type == "PERCENTAGE":
            return PercentageStrategy(strategy_value)
        else:
            raise ValidationException(f"Unknown strategy type: {strategy_type}")
