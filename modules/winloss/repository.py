"""Repository for game records (win/loss tracking)"""

from mysql.connector import Error
from decimal import Decimal
from config.database import DatabaseConnection
from core.logger import logger
from core.exceptions import DatabaseException


class GameRecordsRepository:
    """Database operations for game records"""
    
    @staticmethod
    def save_game_record(session_id: int, gambler_id: int, bet_id: int,
                        outcome: str, stake_before: Decimal, stake_after: Decimal,
                        net_change: Decimal, payout_amount: Decimal = None,
                        loss_amount: Decimal = None, win_streak: int = 0,
                        loss_streak: int = 0):
        """Save a game record after bet outcome"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            query = """
            INSERT INTO game_records 
            (session_id, bet_id, gambler_id, outcome, payout_amount, loss_amount, net_change,
             stake_before, stake_after, consecutive_win_streak, consecutive_loss_streak)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (session_id, bet_id, gambler_id, outcome, payout_amount, loss_amount,
                     net_change, stake_before, stake_after, win_streak, loss_streak)
            
            cursor.execute(query, values)
            connection.commit()
            
            game_id = cursor.lastrowid
            logger.info(f"Game record saved: game_id={game_id}, outcome={outcome}, "
                       f"stake_before={stake_before}, stake_after={stake_after}")
            
            return game_id
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error saving game record: {e}")
            raise DatabaseException(f"Error saving game record: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_session_stats(session_id: int):
        """Get win/loss statistics for a session"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                COUNT(*) as total_games,
                SUM(CASE WHEN outcome = 'WIN' THEN 1 ELSE 0 END) as total_wins,
                SUM(CASE WHEN outcome = 'LOSS' THEN 1 ELSE 0 END) as total_losses,
                MAX(consecutive_win_streak) as max_win_streak,
                MAX(consecutive_loss_streak) as max_loss_streak,
                SUM(net_change) as total_net_change
            FROM game_records
            WHERE session_id = %s
            """
            
            cursor.execute(query, (session_id,))
            result = cursor.fetchone()
            
            return result or {
                'total_games': 0,
                'total_wins': 0,
                'total_losses': 0,
                'max_win_streak': 0,
                'max_loss_streak': 0,
                'total_net_change': Decimal(0)
            }
        
        except Error as e:
            logger.error(f"Error retrieving session stats: {e}")
            raise DatabaseException(f"Error retrieving session stats: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_gambler_stats(gambler_id: int):
        """Get overall win/loss statistics for a gambler"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                COUNT(*) as total_games,
                SUM(CASE WHEN outcome = 'WIN' THEN 1 ELSE 0 END) as total_wins,
                SUM(CASE WHEN outcome = 'LOSS' THEN 1 ELSE 0 END) as total_losses,
                SUM(net_change) as total_net_change
            FROM game_records
            WHERE gambler_id = %s
            """
            
            cursor.execute(query, (gambler_id,))
            result = cursor.fetchone()
            
            return result or {
                'total_games': 0,
                'total_wins': 0,
                'total_losses': 0,
                'total_net_change': Decimal(0)
            }
        
        except Error as e:
            logger.error(f"Error retrieving gambler stats: {e}")
            raise DatabaseException(f"Error retrieving gambler stats: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
