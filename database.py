"""
-What does this file now own?

database.py
│
├── database URL → imported from config
├── engine
└── database table creation
"""

from sqlmodel import SQLModel, create_engine, Session
from config import DATABASE_URL

engine=create_engine(DATABASE_URL)

# def create_db_and_table(): Alembic take care of this
#     SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session