from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

# Railway connection validation is handled by pool_pre_ping=True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()