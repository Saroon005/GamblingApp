from mysql.connector import Error
from decimal import Decimal
from config.database import DatabaseConnection
from core.logger import logger
from core.exceptions import DatabaseException, StakeNotFoundException
import uuid


class StakeRepository:
    
    @staticmethod
    def create_initial_transaction(gambler_id: int, initial_balance: Decimal):
        """Create initial stake transaction for gambler"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            transaction_ref = f"INIT_{gambler_id}_{uuid.uuid4().hex[:8]}"
            
            query = """
            INSERT INTO stake_transactions 
            (gambler_id, transaction_type, amount, balance_before, balance_after, transaction_ref, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            
            values = (
                gambler_id,
                "INITIAL_STAKE",
                initial_balance,
                Decimal("0.00"),
                initial_balance,
                transaction_ref
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            transaction_id = cursor.lastrowid
            logger.info(f"Initial stake transaction created for gambler {gambler_id}: {transaction_id}")
            
            return StakeRepository.get_transaction_by_id(transaction_id)
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error creating initial stake transaction: {e}")
            raise DatabaseException(f"Error creating initial stake transaction: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def record_bet_outcome(gambler_id: int, bet_amount: Decimal, is_win: bool, 
                          balance_before: Decimal, bet_id: int = None, game_id: int = None):
        """Record bet win or loss transaction"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            transaction_type = "BET_WIN" if is_win else "BET_LOSS"
            
            # Calculate balance_after
            if is_win:
                balance_after = balance_before + bet_amount
            else:
                balance_after = balance_before - bet_amount
            
            transaction_ref = f"{transaction_type}_{gambler_id}_{uuid.uuid4().hex[:8]}"
            
            query = """
            INSERT INTO stake_transactions 
            (gambler_id, session_id, bet_id, game_id, transaction_type, amount, 
             balance_before, balance_after, transaction_ref, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            values = (
                gambler_id,
                None,  # session_id
                bet_id,
                game_id,
                transaction_type,
                bet_amount,
                balance_before,
                balance_after,
                transaction_ref
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            transaction_id = cursor.lastrowid
            logger.info(f"Bet outcome transaction recorded for gambler {gambler_id}: {transaction_type} - ${bet_amount}")
            
            return StakeRepository.get_transaction_by_id(transaction_id)
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error recording bet outcome: {e}")
            raise DatabaseException(f"Error recording bet outcome: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def record_deposit(gambler_id: int, amount: Decimal, balance_before: Decimal):
        """Record deposit transaction"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            balance_after = balance_before + amount
            transaction_ref = f"DEPOSIT_{gambler_id}_{uuid.uuid4().hex[:8]}"
            
            query = """
            INSERT INTO stake_transactions 
            (gambler_id, transaction_type, amount, balance_before, balance_after, transaction_ref, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            
            values = (
                gambler_id,
                "DEPOSIT",
                amount,
                balance_before,
                balance_after,
                transaction_ref
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            transaction_id = cursor.lastrowid
            logger.info(f"Deposit transaction recorded for gambler {gambler_id}: ${amount}")
            
            return StakeRepository.get_transaction_by_id(transaction_id)
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error recording deposit: {e}")
            raise DatabaseException(f"Error recording deposit: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def record_withdrawal(gambler_id: int, amount: Decimal, balance_before: Decimal):
        """Record withdrawal transaction"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            balance_after = balance_before - amount
            transaction_ref = f"WITHDRAWAL_{gambler_id}_{uuid.uuid4().hex[:8]}"
            
            query = """
            INSERT INTO stake_transactions 
            (gambler_id, transaction_type, amount, balance_before, balance_after, transaction_ref, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            
            values = (
                gambler_id,
                "WITHDRAWAL",
                amount,
                balance_before,
                balance_after,
                transaction_ref
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            transaction_id = cursor.lastrowid
            logger.info(f"Withdrawal transaction recorded for gambler {gambler_id}: ${amount}")
            
            return StakeRepository.get_transaction_by_id(transaction_id)
        
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error recording withdrawal: {e}")
            raise DatabaseException(f"Error recording withdrawal: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_transaction_by_id(transaction_id: int):
        """Retrieve transaction by ID"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = "SELECT * FROM stake_transactions WHERE transaction_id = %s"
            cursor.execute(query, (transaction_id,))
            
            result = cursor.fetchone()
            if not result:
                raise StakeNotFoundException(f"Transaction with ID {transaction_id} not found")
            
            return result
        
        except Error as e:
            logger.error(f"Error retrieving transaction: {e}")
            raise DatabaseException(f"Error retrieving transaction: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_latest_balance(gambler_id: int) -> Decimal:
        """Get latest balance for gambler from most recent transaction"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT balance_after 
            FROM stake_transactions 
            WHERE gambler_id = %s 
            ORDER BY created_at DESC, transaction_id DESC 
            LIMIT 1
            """
            
            cursor.execute(query, (gambler_id,))
            result = cursor.fetchone()
            
            if not result:
                raise StakeNotFoundException(f"No stake transactions found for gambler {gambler_id}")
            
            return result['balance_after']
        
        except Error as e:
            logger.error(f"Error retrieving latest balance: {e}")
            raise DatabaseException(f"Error retrieving latest balance: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_stake_history(gambler_id: int, transaction_type: str = None, limit: int = None):
        """Retrieve all transactions for a gambler"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            if transaction_type:
                query = """
                SELECT * FROM stake_transactions 
                WHERE gambler_id = %s AND transaction_type = %s
                ORDER BY created_at DESC, transaction_id DESC
                """
                params = (gambler_id, transaction_type)
            else:
                query = """
                SELECT * FROM stake_transactions 
                WHERE gambler_id = %s
                ORDER BY created_at DESC, transaction_id DESC
                """
                params = (gambler_id,)
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            if not results:
                logger.warning(f"No stake transactions found for gambler {gambler_id}")
            
            return results
        
        except Error as e:
            logger.error(f"Error retrieving stake history: {e}")
            raise DatabaseException(f"Error retrieving stake history: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_all_transactions_for_analysis(gambler_id: int):
        """Get all transactions for a gambler for analysis (peak, low, etc)"""
        connection = None
        try:
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT * FROM stake_transactions 
            WHERE gambler_id = %s
            ORDER BY created_at ASC, transaction_id ASC
            """
            
            cursor.execute(query, (gambler_id,))
            results = cursor.fetchall()
            
            return results
        
        except Error as e:
            logger.error(f"Error retrieving transactions for analysis: {e}")
            raise DatabaseException(f"Error retrieving transactions for analysis: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()
