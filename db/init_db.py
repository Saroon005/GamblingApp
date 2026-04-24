import mysql.connector
from mysql.connector import Error
from config.settings import settings
from config.database import DatabaseConnection
from core.logger import logger


class Database:
    @staticmethod
    def create_database():
        """Create database if not exists"""
        connection = None
        cursor = None
        try:
            logger.info(f"\n→ Creating database '{settings.DB_NAME}' if not exists...")
            
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            create_db_query = f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME}"
            cursor.execute(create_db_query)
            connection.commit()
            
            logger.info(f"✓ Database '{settings.DB_NAME}' ready")
        
        except Error as e:
            logger.error(f"✗ Error creating database: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def create_tables():
        """Create tables in the database"""
        connection = None
        cursor = None
        try:
            logger.info(f"\n→ Creating tables...")
            
            connection = DatabaseConnection.get_db_connection()
            cursor = connection.cursor()
            
            create_gambler_table = """
            CREATE TABLE IF NOT EXISTS gambler (
                gambler_id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                initial_stake DECIMAL(10, 2) NOT NULL,
                current_stake DECIMAL(10, 2) NOT NULL,
                win_threshold DECIMAL(10, 2) NOT NULL,
                loss_threshold DECIMAL(10, 2) NOT NULL,
                min_required_stake DECIMAL(10, 2) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            cursor.execute(create_gambler_table)
            connection.commit()
            
            logger.info("✓ Table 'gambler' ready")
            
            create_stake_transactions_table = """
            CREATE TABLE IF NOT EXISTS stake_transactions (
                transaction_id INT PRIMARY KEY AUTO_INCREMENT,
                gambler_id INT NOT NULL,
                session_id INT,
                bet_id INT,
                game_id INT,
                transaction_type VARCHAR(50) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                balance_before DECIMAL(10, 2) NOT NULL,
                balance_after DECIMAL(10, 2) NOT NULL,
                transaction_ref VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (gambler_id) REFERENCES gambler(gambler_id) ON DELETE CASCADE,
                INDEX idx_gambler_id (gambler_id),
                INDEX idx_created_at (created_at)
            )
            """
            
            cursor.execute(create_stake_transactions_table)
            connection.commit()
            
            logger.info("✓ Table 'stake_transactions' ready")
            
            create_bets_table = """
            CREATE TABLE IF NOT EXISTS bets (
                bet_id INT PRIMARY KEY AUTO_INCREMENT,
                gambler_id INT NOT NULL,
                session_id INT,
                strategy_id INT,
                game_index INT NOT NULL,
                bet_amount DECIMAL(10, 2) NOT NULL,
                win_probability DECIMAL(5, 4) NOT NULL,
                odds_type VARCHAR(50),
                odds_value DECIMAL(10, 4),
                potential_win DECIMAL(10, 2),
                stake_before DECIMAL(10, 2) NOT NULL,
                is_settled BOOLEAN DEFAULT FALSE,
                bet_result VARCHAR(20),
                placed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                settled_at DATETIME,
                FOREIGN KEY (gambler_id) REFERENCES gambler(gambler_id) ON DELETE CASCADE,
                INDEX idx_gambler_id (gambler_id),
                INDEX idx_placed_at (placed_at)
            )
            """
            
            cursor.execute(create_bets_table)
            connection.commit()
            
            logger.info("✓ Table 'bets' ready")
        
        except Error as e:
            logger.error(f"✗ Error creating table: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def init():
        """Initialize database and tables"""
        logger.info("\n" + "="*60)
        logger.info("DATABASE INITIALIZATION")
        logger.info("="*60)
        
        try:
            Database.create_database()
            Database.create_tables()
            
            logger.info("\n" + "="*60)
            logger.info("✓ DATABASE INITIALIZATION COMPLETE")
            logger.info("="*60 + "\n")
        
        except Exception as e:
            logger.error(f"\n✗ DATABASE INITIALIZATION FAILED: {e}\n")
            raise

