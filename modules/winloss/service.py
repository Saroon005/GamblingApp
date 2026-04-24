"""Service for win/loss calculation and tracking"""

from decimal import Decimal
from core.logger import logger
from core.exceptions import DatabaseException
from modules.winloss.repository import GameRecordsRepository


class WinLossService:
    """Calculate and track wins, losses, and streaks"""
    
    def __init__(self):
        """Initialize session tracking state"""
        self.win_streak = 0
        self.loss_streak = 0
        self.total_wins = 0
        self.total_losses = 0
        self.games = []
    
    def record_game_outcome(self, session_id: int, gambler_id: int, bet_id: int,
                           is_win: bool, bet_amount: Decimal, 
                           stake_before: Decimal, stake_after: Decimal):
        """Record a game outcome and calculate streaks"""
        
        outcome = "WIN" if is_win else "LOSS"
        net_change = stake_after - stake_before
        payout_amount = None
        loss_amount = None
        
        if is_win:
            self.total_wins += 1
            self.win_streak += 1
            self.loss_streak = 0
            payout_amount = bet_amount
        else:
            self.total_losses += 1
            self.loss_streak += 1
            self.win_streak = 0
            loss_amount = bet_amount
        
        logger.info(f"Game recorded: outcome={outcome}, win_streak={self.win_streak}, "
                   f"loss_streak={self.loss_streak}")
        
        # Save to database
        try:
            game_id = GameRecordsRepository.save_game_record(
                session_id=session_id,
                gambler_id=gambler_id,
                bet_id=bet_id,
                outcome=outcome,
                stake_before=stake_before,
                stake_after=stake_after,
                net_change=net_change,
                payout_amount=payout_amount,
                loss_amount=loss_amount,
                win_streak=self.win_streak,
                loss_streak=self.loss_streak
            )
            
            return {
                'game_id': game_id,
                'outcome': outcome,
                'win_streak': self.win_streak,
                'loss_streak': self.loss_streak,
                'total_wins': self.total_wins,
                'total_losses': self.total_losses,
                'net_change': net_change
            }
        
        except DatabaseException as e:
            logger.error(f"Error recording game outcome: {e}")
            raise
    
    def get_session_summary(self, session_id: int):
        """Get current session stats"""
        total_games = self.total_wins + self.total_losses
        win_rate = (self.total_wins / total_games * 100) if total_games > 0 else 0.0
        
        try:
            db_stats = GameRecordsRepository.get_session_stats(session_id)
            
            return {
                'total_games': total_games,
                'total_wins': self.total_wins,
                'total_losses': self.total_losses,
                'win_rate': round(win_rate, 2),
                'current_win_streak': self.win_streak,
                'current_loss_streak': self.loss_streak,
                'max_win_streak': db_stats.get('max_win_streak', self.win_streak),
                'max_loss_streak': db_stats.get('max_loss_streak', self.loss_streak)
            }
        
        except Exception as e:
            logger.error(f"Error getting session summary: {e}")
            return {
                'total_games': total_games,
                'total_wins': self.total_wins,
                'total_losses': self.total_losses,
                'win_rate': round(win_rate, 2),
                'current_win_streak': self.win_streak,
                'current_loss_streak': self.loss_streak
            }
    
    @staticmethod
    def get_gambler_overall_stats(gambler_id: int):
        """Get overall win/loss statistics for a gambler"""
        try:
            stats = GameRecordsRepository.get_gambler_stats(gambler_id)
            
            total_games = stats.get('total_games', 0)
            total_wins = stats.get('total_wins', 0)
            total_losses = stats.get('total_losses', 0)
            
            win_rate = (total_wins / total_games * 100) if total_games > 0 else 0.0
            
            return {
                'total_games': total_games,
                'total_wins': total_wins,
                'total_losses': total_losses,
                'win_rate': round(win_rate, 2),
                'total_net_change': stats.get('total_net_change', Decimal(0))
            }
        
        except DatabaseException as e:
            logger.error(f"Error getting gambler stats: {e}")
            raise
