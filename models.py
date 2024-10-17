# models.py

from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config

engine = create_engine(config.DATABASE_URI)
Base = declarative_base()

class PageData(Base):
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    timestamp = Column(String)
    url = Column(String, unique=True)
    title = Column(String)
    content = Column(Text)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
