import mysql.connector
from mysql.connector import Error
from config.settings import settings
from core.logger import logger


class DatabaseConnection:
    @staticmethod
    def get_connection():
        """Connect to MySQL server WITHOUT database selection"""
        connection = None
        try:
            logger.info(f"Connecting to MySQL server at {settings.DB_HOST}:{settings.DB_PORT} as {settings.DB_USER}")
            
            connection = mysql.connector.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                autocommit=True
            )
            
            logger.info("✓ Successfully connected to MySQL server")
            return connection
        
        except Error as e:
            logger.error(f"✗ Failed to connect to MySQL server: {e}")
            logger.error("Make sure MySQL server is running on localhost:3306")
            raise
    
    @staticmethod
    def get_db_connection():
        """Connect to MySQL server WITH database selection"""
        connection = None
        try:
            logger.info(f"Connecting to database '{settings.DB_NAME}' at {settings.DB_HOST}:{settings.DB_PORT}")
            
            connection = mysql.connector.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                autocommit=False
            )
            
            logger.info(f"✓ Successfully connected to database '{settings.DB_NAME}'")
            return connection
        
        except Error as e:
            logger.error(f"✗ Failed to connect to database: {e}")
            raise

