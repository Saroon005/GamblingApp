from mysql.connector import Error
from decimal import Decimal
from config.database import DatabaseConnection
from core.logger import logger
from core.exceptions import DatabaseException, GamblerNotFoundException


class GamblerRepository:
    @staticmethod
    def create(gambler_data):
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            query = """
            INSERT INTO gambler 
            (username, full_name, email, is_active, initial_stake, current_stake, 
             win_threshold, loss_threshold, min_required_stake, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            
            values = (
                gambler_data.username,
                gambler_data.full_name,
                gambler_data.email,
                True,
                gambler_data.initial_stake,
                gambler_data.initial_stake,
                gambler_data.win_threshold,
                gambler_data.loss_threshold,
                gambler_data.min_required_stake
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            gambler_id = cursor.lastrowid
            logger.info(f"Gambler created with ID: {gambler_id}")
            
            return GamblerRepository.get_by_id(gambler_id)
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error creating gambler: {e}")
            raise DatabaseException(f"Error creating gambler: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_by_id(gambler_id: int):
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM gambler WHERE gambler_id = %s"
            cursor.execute(query, (gambler_id,))
            
            result = cursor.fetchone()
            if not result:
                raise GamblerNotFoundException(f"Gambler with ID {gambler_id} not found")
            
            return result
        
        except Error as e:
            logger.error(f"Error retrieving gambler: {e}")
            raise DatabaseException(f"Error retrieving gambler: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_by_username(username: str):
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM gambler WHERE username = %s"
            cursor.execute(query, (username,))
            
            result = cursor.fetchone()
            if not result:
                raise GamblerNotFoundException(f"Gambler with username {username} not found")
            
            return result
        
        except Error as e:
            logger.error(f"Error retrieving gambler: {e}")
            raise DatabaseException(f"Error retrieving gambler: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def update(gambler_id: int, update_data):
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            updates = []
            values = []
            
            if update_data.full_name:
                updates.append("full_name = %s")
                values.append(update_data.full_name)
            
            if update_data.email:
                updates.append("email = %s")
                values.append(update_data.email)
            
            if update_data.win_threshold is not None:
                updates.append("win_threshold = %s")
                values.append(update_data.win_threshold)
            
            if update_data.loss_threshold is not None:
                updates.append("loss_threshold = %s")
                values.append(update_data.loss_threshold)
            
            if update_data.min_required_stake is not None:
                updates.append("min_required_stake = %s")
                values.append(update_data.min_required_stake)
            
            if update_data.is_active is not None:
                updates.append("is_active = %s")
                values.append(update_data.is_active)
            
            if not updates:
                return GamblerRepository.get_by_id(gambler_id)
            
            updates.append("updated_at = NOW()")
            values.append(gambler_id)
            
            query = f"UPDATE gambler SET {', '.join(updates)} WHERE gambler_id = %s"
            cursor.execute(query, values)
            connection.commit()
            
            logger.info(f"Gambler {gambler_id} updated successfully")
            
            return GamblerRepository.get_by_id(gambler_id)
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error updating gambler: {e}")
            raise DatabaseException(f"Error updating gambler: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def reset(gambler_id: int):
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            # Get current gambler data
            gambler = GamblerRepository.get_by_id(gambler_id)
            
            initial_stake = gambler['initial_stake']
            new_win_threshold = initial_stake * Decimal(2)
            new_loss_threshold = initial_stake * Decimal('0.5')
            
            query = """
            UPDATE gambler 
            SET current_stake = %s, 
                win_threshold = %s, 
                loss_threshold = %s, 
                updated_at = NOW()
            WHERE gambler_id = %s
            """
            
            values = (initial_stake, new_win_threshold, new_loss_threshold, gambler_id)
            cursor.execute(query, values)
            connection.commit()
            
            logger.info(f"Gambler {gambler_id} profile reset successfully")
            
            return GamblerRepository.get_by_id(gambler_id)
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error resetting gambler: {e}")
            raise DatabaseException(f"Error resetting gambler: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
