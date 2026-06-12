from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
from .config import settings

# 1. SQLAlchemy Connection (Perfect as is!)
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Raw Psycopg2 Connection (Fixed to use cloud settings!)
try:
    connection = psycopg2.connect(
        host=settings.database_hostname,
        database=settings.database_name,
        user=settings.database_username,
        password=settings.database_password,
        port=settings.database_port,
        cursor_factory=RealDictCursor
    )
    cursor = connection.cursor()
    print("DataBase connection was successful!")
except Exception as error:
    print("Connection to the Database Failed")
    print(error)