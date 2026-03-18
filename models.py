from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.testing.suite.test_reflection import users

from database import Base
from sqlalchemy import Float

class User(Base):
    __tablename__= "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable= False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    clients = relationship("User", back_populates="trainer", foreign_keys="trainer_id")
    trainer = relationship("User", back_populates= "clients", remote_side=[id])
    client_plans = relationship("Plan", back_populates="client", foreign_keys="Plan.client_id")
    trainer_plans = relationship("Plan", back_populates="trainer", foreign_keys="Plan.trainer_id")
    invites = relationship("Invite", back_populates="trainer")

class Invite(Base):
    __tablename__="invites"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, nullable=False, unique=True)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),  nullable=False)
    expires_at = Column(DateTime)
    trainer = relationship("User", back_populates="invites")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    plan_type = Column(String, nullable=False)
    start_date = Column(Date, nullable=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    meals = relationship("Meal", back_populates="plan", cascade="all, delete-orphan")
    client = relationship("User", back_populates="client_plans", foreign_keys=[client_id])
    trainer = relationship("User", back_populates="trainer_plans", foreign_keys=[trainer_id])


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "plan_type": self.plan_type,
            "start_date": self.start_date.isoformat() if self.start_date else None
    }

class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    day_number = Column(Integer, nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"))

    plan = relationship("Plan", back_populates="meals")
    foods = relationship("Food", back_populates="meal", cascade="all, delete-orphan")

    @property
    def total_calories(self):
        if not self.foods:
            return 0
        return sum(f.grams * f.food_norm.calories_per_g for f in self.foods)

    @property
    def total_protein(self):
        if not self.foods:
            return 0
        return sum(f.grams * f.food_norm.protein_per_g for f in self.foods)

    @property
    def total_fat(self):
        if not self.foods:
            return 0
        return sum(f.grams * f.food_norm.fat_per_g for f in self.foods)

    @property
    def total_carbs(self):
        if not self.foods:
            return 0
        return sum(f.grams * f.food_norm.carbs_per_g for f in self.foods)




    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "plan_id": self.plan_id,
            "day_number": self.day_number,
            "total_calories": 0,
            "total_protein": 0,
            "total_fat": 0,
            "total_carbs": 0,
        }



class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True)
    grams = Column(Float, nullable=False)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    food_norm_id = Column(Integer, ForeignKey("food_norms.id"), nullable=False)

    meal = relationship("Meal", back_populates="foods")
    food_norm = relationship("FoodNorm", back_populates="foods")

    def to_dict(self):
        return {
            "id": self.id,
            "grams": self.grams,
            "meal_id": self.meal_id,
            "food_norm": self.food_norm.to_dict(),
        }


class FoodNorm(Base):
    __tablename__ = "food_norms"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    calories_per_g = Column(Float)
    protein_per_g = Column(Float)
    carbs_per_g = Column(Float)
    fat_per_g = Column(Float)

    foods = relationship("Food", back_populates="food_norm")


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "calories_per_g": self.calories_per_g,
            "protein_per_g": self.protein_per_g,
            "carbs_per_g": self.carbs_per_g,
            "fat_per_g": self.fat_per_g,

        }