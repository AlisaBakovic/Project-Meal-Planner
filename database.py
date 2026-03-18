from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

engine = create_engine("sqlite:///mealplanner.db")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

