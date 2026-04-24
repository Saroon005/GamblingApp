from mysql.connector import Error
from decimal import Decimal
from config.database import DatabaseConnection
from core.logger import logger
from core.exceptions import DatabaseException


class SessionRepository:
    """Simple repository for session database operations"""
    
    @staticmethod
    def create_session(gambler_id: int, starting_stake: Decimal):
        """Create a new session"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            query = """
            INSERT INTO sessions (gambler_id, status, starting_stake, games_played, started_at)
            VALUES (%s, %s, %s, %s, NOW())
            """
            
            values = (gambler_id, "ACTIVE", starting_stake, 0)
            cursor.execute(query, values)
            connection.commit()
            
            session_id = cursor.lastrowid
            logger.info(f"Session created: session_id={session_id}, gambler_id={gambler_id}, starting_stake={starting_stake}")
            
            return session_id
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error creating session: {e}")
            raise DatabaseException(f"Error creating session: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def end_session(session_id: int, end_reason: str, ending_stake: Decimal):
        """End a session"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            query = """
            UPDATE sessions 
            SET status = %s, end_reason = %s, ending_stake = %s, ended_at = NOW()
            WHERE session_id = %s
            """
            
            values = ("ENDED", end_reason, ending_stake, session_id)
            cursor.execute(query, values)
            connection.commit()
            
            logger.info(f"Session ended: session_id={session_id}, reason={end_reason}, ending_stake={ending_stake}")
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error ending session: {e}")
            raise DatabaseException(f"Error ending session: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_active_session(gambler_id: int):
        """Get active session for gambler"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM sessions WHERE gambler_id = %s AND status = %s"
            cursor.execute(query, (gambler_id, "ACTIVE"))
            
            result = cursor.fetchone()
            return result
        
        except Error as e:
            logger.error(f"Error retrieving active session: {e}")
            raise DatabaseException(f"Error retrieving active session: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def increment_games_played(session_id: int):
        """Increment games played count"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            query = "UPDATE sessions SET games_played = games_played + 1 WHERE session_id = %s"
            cursor.execute(query, (session_id,))
            connection.commit()
            
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error incrementing games played: {e}")
            raise DatabaseException(f"Error incrementing games played: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_session(session_id: int):
        """Get session by ID"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM sessions WHERE session_id = %s"
            cursor.execute(query, (session_id,))
            
            result = cursor.fetchone()
            return result
        
        except Error as e:
            logger.error(f"Error retrieving session: {e}")
            raise DatabaseException(f"Error retrieving session: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
