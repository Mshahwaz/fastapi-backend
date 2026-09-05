"""
-What does this file now own?

database.py
│
├── database URL → imported from config
├── engine
└── database table creation
"""

from sqlmodel import SQLModel, create_engine
from config import DATABASE_URL

engine=create_engine(DATABASE_URL)

def create_db_and_table():
    SQLModel.metadata.create_all(engine)