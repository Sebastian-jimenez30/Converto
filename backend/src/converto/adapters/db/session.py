from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def build_session_factory(database_url: str) -> sessionmaker:
    engine = create_engine(database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)

