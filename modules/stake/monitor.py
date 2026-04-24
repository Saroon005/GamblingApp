from decimal import Decimal
from modules.stake.repository import StakeRepository
from core.logger import logger
from core.exceptions import StakeNotFoundException


class StakeMonitor:
    """Monitor stake fluctuations, peaks, and lows"""
    
    @staticmethod
    def get_peak_stake(gambler_id: int) -> Decimal:
        """Get the highest stake balance for a gambler"""
        try:
            transactions = StakeRepository.get_all_transactions_for_analysis(gambler_id)
            
            if not transactions:
                raise StakeNotFoundException(f"No stake transactions found for gambler {gambler_id}")
            
            peak = max(t['balance_after'] for t in transactions)
            logger.info(f"Peak stake for gambler {gambler_id}: ${peak}")
            
            return peak
        
        except Exception as e:
            logger.error(f"Error calculating peak stake: {e}")
            raise
    
    @staticmethod
    def get_lowest_stake(gambler_id: int) -> Decimal:
        """Get the lowest stake balance for a gambler"""
        try:
            transactions = StakeRepository.get_all_transactions_for_analysis(gambler_id)
            
            if not transactions:
                raise StakeNotFoundException(f"No stake transactions found for gambler {gambler_id}")
            
            lowest = min(t['balance_after'] for t in transactions)
            logger.info(f"Lowest stake for gambler {gambler_id}: ${lowest}")
            
            return lowest
        
        except Exception as e:
            logger.error(f"Error calculating lowest stake: {e}")
            raise
    
    @staticmethod
    def calculate_volatility(gambler_id: int) -> Decimal:
        """Calculate basic volatility as range (peak - lowest)"""
        try:
            transactions = StakeRepository.get_all_transactions_for_analysis(gambler_id)
            
            if not transactions:
                raise StakeNotFoundException(f"No stake transactions found for gambler {gambler_id}")
            
            balances = [t['balance_after'] for t in transactions]
            peak = max(balances)
            lowest = min(balances)
            
            volatility = peak - lowest
            logger.info(f"Volatility for gambler {gambler_id}: ${volatility} (peak: ${peak}, low: ${lowest})")
            
            return volatility
        
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            raise
    
    @staticmethod
    def get_stake_statistics(gambler_id: int) -> dict:
        """Get comprehensive stake statistics"""
        try:
            transactions = StakeRepository.get_all_transactions_for_analysis(gambler_id)
            
            if not transactions:
                raise StakeNotFoundException(f"No stake transactions found for gambler {gambler_id}")
            
            balances = [t['balance_after'] for t in transactions]
            
            peak = max(balances)
            lowest = min(balances)
            current = balances[-1]  # Last balance
            initial = balances[0]  # First balance
            
            volatility = peak - lowest
            net_change = current - initial
            transaction_count = len(transactions)
            
            # Calculate win/loss counts
            win_count = sum(1 for t in transactions if t['transaction_type'] == 'BET_WIN')
            loss_count = sum(1 for t in transactions if t['transaction_type'] == 'BET_LOSS')
            
            stats = {
                'gambler_id': gambler_id,
                'initial_balance': initial,
                'current_balance': current,
                'peak_balance': peak,
                'lowest_balance': lowest,
                'net_change': net_change,
                'volatility': volatility,
                'total_transactions': transaction_count,
                'win_count': win_count,
                'loss_count': loss_count,
                'deposit_count': sum(1 for t in transactions if t['transaction_type'] == 'DEPOSIT'),
                'withdrawal_count': sum(1 for t in transactions if t['transaction_type'] == 'WITHDRAWAL')
            }
            
            logger.info(f"Stake statistics calculated for gambler {gambler_id}")
            return stats
        
        except Exception as e:
            logger.error(f"Error calculating stake statistics: {e}")
            raise
    
    @staticmethod
    def check_threshold_breaches(gambler_id: int, win_threshold: Decimal, loss_threshold: Decimal) -> dict:
        """Check if gambler has breached thresholds"""
        try:
            transactions = StakeRepository.get_all_transactions_for_analysis(gambler_id)
            
            if not transactions:
                raise StakeNotFoundException(f"No stake transactions found for gambler {gambler_id}")
            
            peak = max(t['balance_after'] for t in transactions)
            lowest = min(t['balance_after'] for t in transactions)
            
            win_threshold_breached = peak >= win_threshold
            loss_threshold_breached = lowest <= loss_threshold
            
            result = {
                'gambler_id': gambler_id,
                'win_threshold': win_threshold,
                'loss_threshold': loss_threshold,
                'peak_reached': peak,
                'lowest_reached': lowest,
                'win_threshold_breached': win_threshold_breached,
                'loss_threshold_breached': loss_threshold_breached
            }
            
            if win_threshold_breached:
                logger.warning(f"Gambler {gambler_id} has reached win threshold: ${peak} >= ${win_threshold}")
            
            if loss_threshold_breached:
                logger.warning(f"Gambler {gambler_id} has reached loss threshold: ${lowest} <= ${loss_threshold}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error checking threshold breaches: {e}")
            raise
