import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import logging
import os

load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in the environment

settings = DatabaseSettings()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise

def create_cache_table():
    """Create the cache table if it doesn't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS timetable_cache (
            id SERIAL PRIMARY KEY,
            cache_key VARCHAR(255) UNIQUE NOT NULL,
            cache_data TEXT,
            hash_value VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Cache table created successfully")
    except Exception as e:
        logger.error(f"Error creating cache table: {e}")
        raise

def get_table_from_cache(filename: str, class_pattern: str, is_exam: bool) -> str | None:
    """
    Get a timetable (lecture or exam) from the PostgreSQL cache.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cache_key = f"{filename}-{class_pattern.replace(' ', '')}-{'exam' if is_exam else 'lecture'}"
        
        select_query = """
        SELECT cache_data FROM timetable_cache 
        WHERE cache_key = %s AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        """
        
        cursor.execute(select_query, (cache_key,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return result['cache_data']
        return None
    except Exception as e:
        logger.error(f"Error retrieving from cache: {e}")
        return None

def add_table_to_cache(table: str, filename: str, class_pattern: str, is_exam: bool, expire_seconds: int = 3600):
    """
    Add a timetable (lecture or exam) to the PostgreSQL cache.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cache_key = f"{filename}-{class_pattern.replace(' ', '')}-{'exam' if is_exam else 'lecture'}"
        
        # Calculate expiration time
        from datetime import datetime, timedelta
        expires_at = datetime.now() + timedelta(seconds=expire_seconds)
        
        upsert_query = """
        INSERT INTO timetable_cache (cache_key, cache_data, hash_value, expires_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (cache_key) 
        DO UPDATE SET cache_data = EXCLUDED.cache_data, hash_value = EXCLUDED.hash_value, expires_at = EXCLUDED.expires_at
        """
        
        # For simplicity, we'll use a simple hash of the data as the hash_value
        import hashlib
        hash_value = hashlib.md5(table.encode()).hexdigest()
        
        cursor.execute(upsert_query, (cache_key, table, hash_value, expires_at))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error adding to cache: {e}")