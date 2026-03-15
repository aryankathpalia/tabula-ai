from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create engine with safe connection settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,           # checks connection health
    pool_recycle=300,             # recycle stale connections
    connect_args={
        "connect_timeout": 5,     # fail fast if DB is unreachable
        "sslmode": "require"      # required for Neon
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Optional debug log
print("Database engine initialized")