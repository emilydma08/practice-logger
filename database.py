from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    icon = Column(String)
    username = Column(String, nullable=False)  # Add username to associate with a user
    log_entries = relationship("LogEntry", back_populates="category", cascade="all, delete-orphan", passive_deletes=True)

class LogEntry(Base):
    __tablename__ = 'log_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    date = Column(Date)
    duration = Column(Integer)  # Duration in minutes
    notes = Column(String, nullable=True)
    username = Column(String, nullable=False)  # Add username to associate with a user

    category = relationship("Category", back_populates="log_entries")

def init_db():
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)
