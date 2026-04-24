from decimal import Decimal
from core.logger import logger
from core.exceptions import ValidationException, DatabaseException, StakeNotFoundException
from modules.stake.validator import StakeValidator
from modules.stake.repository import StakeRepository
from modules.stake.monitor import StakeMonitor
from modules.gambler.repository import GamblerRepository


class StakeService:
    
    @staticmethod
    def initialize_stake(gambler_id: int):
        """Initialize starting stake for a gambler while updating gambler's current_stake"""
        logger.info(f"Initializing stake for gambler {gambler_id}")
        
        try:
            # Validate gambler exists and get their data
            gambler = GamblerRepository.get_by_id(gambler_id)
            
            initial_balance = gambler['initial_stake']
            
            # Validate initialization
            StakeValidator.validate_initialization(gambler_id, initial_balance)
            
            # Create initial transaction
            transaction = StakeRepository.create_initial_transaction(gambler_id, initial_balance)
            
            logger.info(f"Stake initialized for gambler {gambler_id}: ${initial_balance}")
            return transaction
        
        except ValidationException:
            raise
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Error initializing stake: {e}")
            raise DatabaseException(f"Error initializing stake: {e}")
    
    @staticmethod
    def get_current_balance(gambler_id: int) -> Decimal:
        """Get current stake balance for a gambler"""
        logger.info(f"Retrieving current balance for gambler {gambler_id}")
        
        try:
            # Validate gambler exists
            GamblerRepository.get_by_id(gambler_id)
            
            # Get latest balance from transactions
            balance = StakeRepository.get_latest_balance(gambler_id)
            
            logger.info(f"Current balance for gambler {gambler_id}: ${balance}")
            return balance
        
        except StakeNotFoundException:
            logger.warning(f"No stake transactions found for gambler {gambler_id}")
            raise
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving current balance: {e}")
            raise DatabaseException(f"Error retrieving current balance: {e}")
    
    @staticmethod
    def process_bet_outcome(gambler_id: int, bet_amount: Decimal, is_win: bool, 
                           bet_id: int = None, game_id: int = None):
        """Process bet outcome (win or loss) and update stake"""
        logger.info(f"Processing bet outcome for gambler {gambler_id}: "
                   f"amount=${bet_amount}, result={'WIN' if is_win else 'LOSS'}")
        
        try:
            # Get current balance
            current_balance = StakeService.get_current_balance(gambler_id)
            
            # Validate bet outcome
            StakeValidator.validate_bet_outcome(gambler_id, bet_amount, is_win, current_balance)
            
            # Record transaction
            transaction = StakeRepository.record_bet_outcome(
                gambler_id=gambler_id,
                bet_amount=bet_amount,
                is_win=is_win,
                balance_before=current_balance,
                bet_id=bet_id,
                game_id=game_id
            )
            
            logger.info(f"Bet outcome processed for gambler {gambler_id}: "
                       f"new balance = ${transaction['balance_after']}")
            return transaction
        
        except ValidationException:
            raise
        except StakeNotFoundException:
            raise
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Error processing bet outcome: {e}")
            raise DatabaseException(f"Error processing bet outcome: {e}")
    
    @staticmethod
    def deposit_stake(gambler_id: int, amount: Decimal):
        """Record a deposit to gambler's stake"""
        logger.info(f"Recording deposit for gambler {gambler_id}: ${amount}")
        
        try:
            # Validate deposit
            StakeValidator.validate_deposit(gambler_id, amount)
            
            # Get current balance
            current_balance = StakeService.get_current_balance(gambler_id)
            
            # Record transaction
            transaction = StakeRepository.record_deposit(gambler_id, amount, current_balance)
            
            logger.info(f"Deposit recorded for gambler {gambler_id}: "
                       f"new balance = ${transaction['balance_after']}")
            return transaction
        
        except ValidationException:
            raise
        except StakeNotFoundException:
            raise
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Error recording deposit: {e}")
            raise DatabaseException(f"Error recording deposit: {e}")
    
    @staticmethod
    def withdraw_stake(gambler_id: int, amount: Decimal):
        """Record a withdrawal from gambler's stake"""
        logger.info(f"Recording withdrawal for gambler {gambler_id}: ${amount}")
        
        try:
            # Get current balance
            current_balance = StakeService.get_current_balance(gambler_id)
            
            # Validate withdrawal
            StakeValidator.validate_withdrawal(gambler_id, amount, current_balance)
            
            # Record transaction
            transaction = StakeRepository.record_withdrawal(gambler_id, amount, current_balance)
            
            logger.info(f"Withdrawal recorded for gambler {gambler_id}: "
                       f"new balance = ${transaction['balance_after']}")
            return transaction
        
        except ValidationException:
            raise
        except StakeNotFoundException:
            raise
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Error recording withdrawal: {e}")
            raise DatabaseException(f"Error recording withdrawal: {e}")
    
    @staticmethod
    def validate_stake_boundaries(gambler_id: int, lower_limit: Decimal = None, 
                                 upper_limit: Decimal = None):
        """Validate current stake is within boundaries"""
        logger.info(f"Validating stake boundaries for gambler {gambler_id}")
        
        try:
            # Get current balance
            current_balance = StakeService.get_current_balance(gambler_id)
            
            # Validate boundaries
            StakeValidator.validate_stake_boundary(current_balance, lower_limit, upper_limit)
            
            logger.info(f"Stake boundaries validated for gambler {gambler_id}")
            return True
        
        except ValidationException as e:
            logger.warning(f"Stake boundary validation failed for gambler {gambler_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error validating stake boundaries: {e}")
            raise DatabaseException(f"Error validating stake boundaries: {e}")
    
    @staticmethod
    def get_stake_history(gambler_id: int, transaction_type: str = None, limit: int = None):
        """Get stake transaction history for a gambler"""
        logger.info(f"Retrieving stake history for gambler {gambler_id}")
        
        try:
            # Validate gambler exists
            GamblerRepository.get_by_id(gambler_id)
            
            # Validate transaction type if provided
            if transaction_type:
                StakeValidator.validate_transaction_type(transaction_type)
            
            # Get history
            history = StakeRepository.get_stake_history(gambler_id, transaction_type, limit)
            
            logger.info(f"Retrieved {len(history)} stake transactions for gambler {gambler_id}")
            return history
        
        except ValidationException:
            raise
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving stake history: {e}")
            raise DatabaseException(f"Error retrieving stake history: {e}")
    
    @staticmethod
    def get_peak_stake(gambler_id: int) -> Decimal:
        """Get peak stake for a gambler"""
        logger.info(f"Retrieving peak stake for gambler {gambler_id}")
        
        try:
            # Validate gambler exists
            GamblerRepository.get_by_id(gambler_id)
            
            peak = StakeMonitor.get_peak_stake(gambler_id)
            
            logger.info(f"Peak stake for gambler {gambler_id}: ${peak}")
            return peak
        
        except Exception:
            raise
    
    @staticmethod
    def get_lowest_stake(gambler_id: int) -> Decimal:
        """Get lowest stake for a gambler"""
        logger.info(f"Retrieving lowest stake for gambler {gambler_id}")
        
        try:
            # Validate gambler exists
            GamblerRepository.get_by_id(gambler_id)
            
            lowest = StakeMonitor.get_lowest_stake(gambler_id)
            
            logger.info(f"Lowest stake for gambler {gambler_id}: ${lowest}")
            return lowest
        
        except Exception:
            raise
    
    @staticmethod
    def get_volatility(gambler_id: int) -> Decimal:
        """Get stake volatility (peak - lowest) for a gambler"""
        logger.info(f"Calculating volatility for gambler {gambler_id}")
        
        try:
            # Validate gambler exists
            GamblerRepository.get_by_id(gambler_id)
            
            volatility = StakeMonitor.calculate_volatility(gambler_id)
            
            logger.info(f"Volatility for gambler {gambler_id}: ${volatility}")
            return volatility
        
        except Exception:
            raise
    
    @staticmethod
    def get_stake_statistics(gambler_id: int) -> dict:
        """Get comprehensive stake statistics"""
        logger.info(f"Generating stake statistics for gambler {gambler_id}")
        
        try:
            # Validate gambler exists
            GamblerRepository.get_by_id(gambler_id)
            
            stats = StakeMonitor.get_stake_statistics(gambler_id)
            
            logger.info(f"Stake statistics generated for gambler {gambler_id}")
            return stats
        
        except Exception:
            raise
    
    @staticmethod
    def check_threshold_breaches(gambler_id: int) -> dict:
        """Check if gambler has breached thresholds from their profile"""
        logger.info(f"Checking threshold breaches for gambler {gambler_id}")
        
        try:
            # Get gambler profile to get thresholds
            gambler = GamblerRepository.get_by_id(gambler_id)
            
            breaches = StakeMonitor.check_threshold_breaches(
                gambler_id,
                gambler['win_threshold'],
                gambler['loss_threshold']
            )
            
            logger.info(f"Threshold check completed for gambler {gambler_id}")
            return breaches
        
        except Exception:
            raise
