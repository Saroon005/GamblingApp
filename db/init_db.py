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

