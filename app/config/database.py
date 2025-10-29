from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DisconnectionError
import time

from app.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    # Railway-optimized connection pool settings
    pool_size=5,              # Reduced for Railway limits
    max_overflow=10,          # Smaller overflow 
    pool_timeout=10,          # Faster timeout to fail fast
    pool_recycle=1800,        # Recycle connections more frequently (30 mins)
    pool_pre_ping=True,       # Validate connections
    echo=settings.DEBUG,      # Enable SQL logging in debug mode
    connect_args={
        "connect_timeout": 10,     # 10 second connection timeout
        "application_name": "zehnly_vocab_service"
    } if "postgresql" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Add connection event listeners for better Railway compatibility
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "postgresql" in settings.DATABASE_URL:
        # Set connection parameters for PostgreSQL on Railway
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET statement_timeout = '30s'")
            cursor.execute("SET idle_in_transaction_session_timeout = '60s'")

@event.listens_for(engine, "engine_connect")
def ping_connection(connection, branch):
    """Ensure connection is alive, reconnect if not"""
    if branch:
        return
    
    try:
        connection.scalar("SELECT 1")
    except Exception as err:
        if isinstance(err, DisconnectionError):
            print(f"Database reconnection required: {err}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()