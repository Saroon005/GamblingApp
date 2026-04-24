from mysql.connector import Error
from decimal import Decimal
from config.database import DatabaseConnection
from core.logger import logger
from core.exceptions import DatabaseException, BetNotFoundException
import uuid


class BettingRepository:
    
    @staticmethod
    def place_bet(gambler_id: int, bet_amount: Decimal, win_probability: float,
                  game_index: int, stake_before: Decimal, odds_type: str = None,
                  odds_value: Decimal = None, strategy_id: int = None):
        """Record a new bet in the database"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            # Calculate potential win (assuming 1:1 odds for now)
            potential_win = bet_amount * Decimal("2")  # Double return (original + winnings)
            
            query = """
            INSERT INTO bets 
            (gambler_id, strategy_id, game_index, bet_amount, win_probability, 
             odds_type, odds_value, potential_win, stake_before, is_settled, placed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            values = (
                gambler_id,
                strategy_id,
                game_index,
                bet_amount,
                win_probability,
                odds_type,
                odds_value,
                potential_win,
                stake_before,
                False
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            bet_id = cursor.lastrowid
            logger.info(f"Bet placed for gambler {gambler_id}: bet_id={bet_id}, amount=${bet_amount}, "
                       f"probability={win_probability:.1%}")
            
            return BettingRepository.get_bet_by_id(bet_id)
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error placing bet: {e}")
            raise DatabaseException(f"Error placing bet: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def settle_bet(bet_id: int, is_win: bool):
        """Settle a bet with win/loss result"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            bet_result = "WIN" if is_win else "LOSS"
            
            query = """
            UPDATE bets 
            SET is_settled = TRUE, bet_result = %s, settled_at = NOW()
            WHERE bet_id = %s
            """
            
            values = (bet_result, bet_id)
            cursor.execute(query, values)
            connection.commit()
            
            logger.info(f"Bet {bet_id} settled: {bet_result}")
            
            return BettingRepository.get_bet_by_id(bet_id)
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error settling bet: {e}")
            raise DatabaseException(f"Error settling bet: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_bet_by_id(bet_id: int):
        """Retrieve a bet by ID"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM bets WHERE bet_id = %s"
            cursor.execute(query, (bet_id,))
            
            result = cursor.fetchone()
            if not result:
                raise BetNotFoundException(f"Bet with ID {bet_id} not found")
            
            return result
        
        except Error as e:
            logger.error(f"Error retrieving bet: {e}")
            raise DatabaseException(f"Error retrieving bet: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_gambler_bets(gambler_id: int, limit: int = None):
        """Retrieve all bets for a gambler"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT * FROM bets 
            WHERE gambler_id = %s
            ORDER BY placed_at DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (gambler_id,))
            results = cursor.fetchall()
            
            logger.info(f"Retrieved {len(results)} bets for gambler {gambler_id}")
            return results
        
        except Error as e:
            logger.error(f"Error retrieving gambler bets: {e}")
            raise DatabaseException(f"Error retrieving gambler bets: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_gambler_bet_statistics(gambler_id: int) -> dict:
        """Get betting statistics for a gambler"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT 
                COUNT(*) as total_bets,
                SUM(CASE WHEN bet_result = 'WIN' THEN 1 ELSE 0 END) as win_count,
                SUM(CASE WHEN bet_result = 'LOSS' THEN 1 ELSE 0 END) as loss_count,
                SUM(CASE WHEN is_settled = FALSE THEN 1 ELSE 0 END) as unsettled_count,
                SUM(bet_amount) as total_wagered,
                AVG(bet_amount) as avg_bet
            FROM bets 
            WHERE gambler_id = %s AND is_settled = TRUE
            """
            
            cursor.execute(query, (gambler_id,))
            result = cursor.fetchone()
            
            return {
                'gambler_id': gambler_id,
                'total_bets': result['total_bets'] or 0,
                'win_count': result['win_count'] or 0,
                'loss_count': result['loss_count'] or 0,
                'unsettled_count': result['unsettled_count'] or 0,
                'total_wagered': result['total_wagered'] or Decimal("0.00"),
                'avg_bet': result['avg_bet'] or Decimal("0.00")
            }
        
        except Error as e:
            logger.error(f"Error retrieving betting statistics: {e}")
            raise DatabaseException(f"Error retrieving betting statistics: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
