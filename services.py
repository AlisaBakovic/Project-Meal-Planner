from datetime import datetime

from flask import session
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from auth import generate_token
from database import SessionLocal
from models import Plan, Meal, User, FoodNorm, Food


def register_trainer(email, password, first_name, last_name):
    session = SessionLocal()

    try:
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("This email already exists!")

        hashed_password = generate_password_hash(password)

        user = User(
            email=email,
            password_hash=hashed_password,
            role="trainer",
            first_name=first_name,
            last_name=last_name,
            trainer_id=None,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user.to_dict()

    finally:
        session.close()

def login_user(email, password):

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("Invalid email or password")

        if not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid email or password")

        token = generate_token(user)

        return token

    finally:
        session.close()

def create_plan(name, plan_type, client_id, trainer_id, start_date=None):
    session = SessionLocal()

    try:
        if plan_type not in ["calendar", "template"]:
            raise ValueError("Invalid plan type")

        if plan_type == "calendar" and not start_date:
            raise ValueError("Calendar plan type requires start_date")

        if plan_type == "template" and start_date:
            raise ValueError("Template plan cannot have start_date")

        if start_date:
            start_date = datetime.fromisoformat(start_date).date()
        else:
            start_date = None

        client = session.query(User).filter(User.id == client_id).first()

        if not client:
            raise ValueError("Client not found")
        if client.trainer_id != trainer_id:
            raise ValueError("This client does not belong to this trainer")

        plan = Plan(
            name=name,
            plan_type=plan_type,
            start_date=start_date,
            client_id=client_id,
            trainer_id=trainer_id,
        )

        session.add(plan)
        session.commit()
        session.refresh(plan)

        return plan.to_dict()

    finally:
        session.close()

def get_plans(user):

    session = SessionLocal()
    try:
        if user.role == "trainer":
            plans = session.query(Plan).filter(Plan.trainer_id == user.id).all()
        elif user.role == "client":
            plans = session.query(Plan).filter(Plan.client_id == user.id).all()
        else:
            raise ValueError("Undefined user")

        return [p.to_dict() for p in plans]

    finally:
        session.close()

def get_plan_by_id(plan_id):
    session = SessionLocal()

    try:
        plan = session.get(Plan, plan_id)

        if not plan:
            return None

        return plan.to_dict()

    finally:
        session.close()


def delete_plan(plan_id):

    session = SessionLocal()

    try:
        plan = session.query(Plan).filter(Plan.id == plan_id).first()

        if not plan:
            raise ValueError("Plan not found")
        session.delete(plan)
        session.commit()

        return plan.to_dict()

    finally:
        session.close()

def update_plan(plan_id, name, plan_type, client_id, start_date=None):

    session = SessionLocal()

    try:
        plan = session.query(Plan).filter(Plan.id == plan_id).first()

        if not plan:
            raise ValueError("Plan not found")
        if plan_type not in ["calendar", "template"]:
            raise ValueError("Invalid plan type")
        if plan_type == "calendar" and not start_date:
            raise ValueError("Calendar plan type requires start_date")
        if plan_type == "template" and start_date:
            raise ValueError("Template plan cannot have start_date")

        if start_date:
            start_date = datetime.fromisoformat(start_date).date()
        else:
            start_date = None

        plan.name = name
        plan.plan_type = plan_type
        plan.client_id = client_id
        plan.start_date = start_date

        session.commit()
        session.refresh(plan)

        return plan.to_dict()

    finally:
        session.close()




def create_meal(name, plan_id, day_number):

    session = SessionLocal()

    try:

        if day_number <= 0:
            raise ValueError("Day can not be zero or negative")
        meal = Meal(name=name, plan_id=plan_id, day_number=day_number)

        session.add(meal)
        session.commit()
        session.refresh(meal)

        return meal.to_dict()

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()

def get_meals_for_plan(plan_id):

    session = SessionLocal()

    try:
        plan = session.get(Plan, plan_id)

        if not plan:
            return []

        meals = [m.to_dict() for m in plan.meals]

        return meals

    finally:
        session.close()

def delete_meal(meal_id):

    session = SessionLocal()

    try:
        meal = session.query(Meal).filter(Meal.id == meal_id).first()

        if not meal:
            raise ValueError("Meal not found")

        meal_data = meal.to_dict()

        session.delete(meal)
        session.commit()

        return meal_data

    finally:
        session.close()

def get_clients_by_trainer(trainer_id):

    session = SessionLocal()

    try:

        clients = (
            session.query(User)
            .filter(User.trainer_id == trainer_id)
            .filter(User.role == "client")
            .all()
        )

        return [c.to_dict() for c in clients]

    finally:
        session.close()

def create_food_norm(user, name, calories, protein, carbs, fat):

    session = SessionLocal()

    try:
        name = name.strip().lower()

        existing = session.query(FoodNorm).filter(FoodNorm.name == name).first()

        if existing:
            raise ValueError("Food already exists.")

        food = FoodNorm(
            name=name,
            created_by=user.id,
            calories_per_g=float(calories or 0) / 100,
            protein_per_g=float(protein or 0) / 100,
            carbs_per_g=float(carbs or 0) / 100,
            fat_per_g=float(fat or 0) / 100,
        )

        session.add(food)
        session.commit()
        session.refresh(food)

        return food.to_dict()

    finally:
        session.close()

def get_food_norms(user):

    session = SessionLocal()

    try:
        foods = (
            session.query(FoodNorm)
            .filter(or_(FoodNorm.created_by.is_(None), FoodNorm.created_by == user.id))
            .all()
        )

        return [f.to_dict() for f in foods]

    finally:
        session.close()

def create_food(meal_id, food_norm_id, grams):

    session = SessionLocal()

    try:
        meal = session.query(Meal).filter(Meal.id == meal_id).first()
        if not meal:
            raise ValueError("Meal not found")

        food_norm = session.query(FoodNorm).filter(FoodNorm.id == food_norm_id).first()
        if not food_norm:
            raise ValueError("Food not found")

        if float(grams) <= 0:
            raise ValueError("Grams must be positive")

        food = Food(meal_id=meal_id, food_norm_id=food_norm_id, grams=grams)

        session.add(food)
        session.commit()
        session.refresh(food)

        return food.to_dict()

    finally:
        session.close()

def delete_food(food_id):

    session = SessionLocal()

    try:
        food = session.query(Food).filter(Food.id == food_id).first()

        if not food:
            raise ValueError("Food not found")

        session.delete(food)
        session.commit()

        return True
    finally:
        session.close()

def update_food(food_id, grams):
    session = SessionLocal()

    try:
        food = session.query(Food).filter(Food.id == food_id).first()

        if not food:
            raise ValueError("Food not found")

        if grams <= 0:
            raise ValueError("Grams must be positive")

        food.grams = grams

        session.commit()
        session.refresh(food)

        result = food.to_dict()
        return result

    finally:
        session.close()