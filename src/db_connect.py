from sqlalchemy import create_engine, Boolean,Column, Integer, String, DECIMAL, Float, Enum, DateTime, Date, ForeignKey, func, case
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pytz 
from datetime import datetime
import re

Base = declarative_base()

class Pool(Base):
    __tablename__ = 'Pool'
    
    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False)
    whatsapp_status = Column(Boolean, default=False)
    created_date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Baku')))
    updated_date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Baku')), 
                                onupdate=lambda: datetime.now(pytz.timezone('Asia/Baku')))


class TempNumbers(Base):
    __tablename__ = 'TempNumbers'
    
    id = Column(Integer, primary_key=True)
    number = Column(String(50), nullable=False)


class License(Base):
    __tablename__ = 'License'

    id = Column(Integer, primary_key=True)
    app_license = Column(String(100), default='no_license_key')
    created_date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Baku')))
    updated_date = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Baku')), 
                                onupdate=lambda: datetime.now(pytz.timezone('Asia/Baku')))


# Create a SQLite database
engine = create_engine('sqlite:///local.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
