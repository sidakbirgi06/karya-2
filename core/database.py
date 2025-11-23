# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Define the database URL. "sqlite:///./app.db" means
# we will use an SQLite database with a file named "app.db"
# in the current directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# 2. Create the SQLAlchemy "engine". This is the main
# connection point to the database.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# The "check_same_thread" argument is needed only for SQLite.

# 3. Create a "Session" class. Each instance of this
# class will be a new database "conversation" (session).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create a "Base" class. Our data models (in models.py)
# will "inherit" from this class. This is how SQLAlchemy's
# magic works to connect our Python classes to database tables.
Base = declarative_base()