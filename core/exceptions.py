class ValidationException(Exception):
    """Custom exception for validation errors"""
    pass


class DatabaseException(Exception):
    """Custom exception for database errors"""
    pass


class GamblerNotFoundException(Exception):
    """Exception raised when gambler is not found"""
    pass


class StakeNotFoundException(Exception):
    """Exception raised when stake/transaction is not found"""
    pass


class InsufficientStakeException(Exception):
    """Exception raised when stake is insufficient"""
    pass


class BetNotFoundException(Exception):
    """Exception raised when bet is not found"""
    pass


class InvalidBetException(Exception):
    """Exception raised when bet is invalid"""
    pass
