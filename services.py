import secrets
from datetime import datetime, timedelta

from flask import session
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from auth import generate_token
from database import SessionLocal
from models import Plan, Meal, User, FoodNorm, Food, Invite, Questionnaire
from dotenv import load_dotenv
import os

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")

def register_trainer(email, password, first_name, last_name):
    session = SessionLocal()

    try:
        existing_user = session.query(User).filter(User.email == email).first()

        if not email.strip():
            raise ValueError("Email is required!")

        if len(password) < 6:
            raise ValueError("Password is to short!")

        if existing_user:
            raise ValueError("This email already exists!")

        if not first_name.strip():
            raise ValueError("First name required!")

        if not last_name.strip():
            raise ValueError("Last name required!")

        hashed_password = generate_password_hash(password)

        user = User(
            email = email.strip().lower(),
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

    email = email.strip().lower()

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        if not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid email or password")

        token = generate_token(user)

        return token, user

    finally:
        session.close()

def create_invite(email, trainer_id):

    session = SessionLocal()

    email = email.strip().lower()

    try:
        existing_client = session.query(User).filter(User.email == email).first()
        if existing_client:
            raise ValueError("This email already exists!")

        existing_invite = session.query(Invite).filter(Invite.used.is_(False), Invite.revoked.is_(False), Invite.email == email).first()
        if existing_invite:
            raise ValueError("This invitation has been already sent!")

        invite = Invite(
            email=email,
            trainer_id=trainer_id,
            used=False,
            expires_at=datetime.utcnow() + timedelta(days=7),
            token=secrets.token_urlsafe(32)
        )

        session.add(invite)
        session.commit()
        session.refresh(invite)

        invite_link = f"{FRONTEND_URL}/invite/{invite.token}"

        return {**invite.to_dict(),
                "invite_link": invite_link}

    finally:
        session.close()

def validate_invite_token(token):

    session = SessionLocal()

    current_time = datetime.utcnow()

    try:
        invite = session.query(Invite).filter(Invite.token == token, Invite.used.is_(False), Invite.revoked.is_(False)).first()
        if not invite:
            raise ValueError("Invalid token!")

        invite_expired = current_time > invite.expires_at
        if invite_expired:
            raise ValueError("Token expired!")

        return invite.to_dict()

    finally:
        session.close()

def accept_invite(token, first_name, last_name, password):

    session = SessionLocal()

    try:
        found_token = session.query(Invite).filter(Invite.token == token).first()
        if not found_token:
            raise ValueError("Invalid token!")

        if len(password) < 6:
            raise ValueError("Password is too short!")

        if not first_name.strip():
            raise ValueError("First name required")

        if not last_name.strip():
            raise ValueError("Last name required")

        validate_invite_token(token)

        hashed_password = generate_password_hash(password)

        client = User(email=found_token.email,
                    password_hash=hashed_password,
                    first_name=first_name,
                    last_name=last_name,
                    role="client",
                    trainer_id=found_token.trainer_id)

        found_token.used = True

        session.add(client)
        session.commit()
        session.refresh(client)

        return client.to_dict()

    finally:
        session.close()

def revoke_invitation(invite_id, trainer_id):

    session = SessionLocal()

    try:
        invite = session.query(Invite).filter(Invite.id == invite_id, Invite.trainer_id == trainer_id).first()

        if not invite:
            raise ValueError("Invitation not found!")

        if invite.revoked:
            raise ValueError("Invitation has already been revoked.")

        invite.revoked = True

        session.commit()
        session.refresh(invite)

        return invite.to_dict()

    finally:
        session.close()


def resend_invitation(invite_id, trainer_id):
    session = SessionLocal()

    try:
        invite = session.query(Invite).filter(Invite.id == invite_id, Invite.trainer_id == trainer_id).first()

        if not invite:
            raise ValueError("Invitation not found!")

        if invite.used:
            raise ValueError("Invitation has already been used.")

        if invite.revoked:
            raise ValueError("Invitation has been revoked.")

        invite.token = secrets.token_urlsafe(32)
        invite.expires_at = datetime.utcnow() + timedelta(days=7)

        invite_link = f"https://meal-planner-frontend-lemon.vercel.app/invite/{invite.token}"

        session.commit()
        session.refresh(invite)

        return {**invite.to_dict(),
                "invite_link": invite_link}

    finally:
        session.close()

def get_invitation(trainer_id):

    session = SessionLocal()

    try:
        invitations = session.query(Invite).filter(Invite.trainer_id == trainer_id, Invite.used == False, Invite.revoked == False).all()

        return [invite.to_dict() for invite in invitations]

    finally:
        session.close()

def create_questionnaire(answers, user):

    session = SessionLocal()

    try:
        if user.role != "client":
            raise ValueError("Not authorized!")

        existing_questionnaire = session.query(Questionnaire).filter(Questionnaire.client_id == user.id).first()

        if existing_questionnaire:
            raise ValueError("This questionnaire already exists!")

        if not answers:
            raise ValueError("Questionnaire answers are required!")

        questionnaire = Questionnaire(
            client_id=user.id,
            editable_until=datetime.utcnow() + timedelta(days=50),
            answers=answers
        )

        session.add(questionnaire)
        session.commit()
        session.refresh(questionnaire)

        return questionnaire.to_dict()


    finally:
        session.close()

def validate_answers(answers):

    if not answers:
        raise ValueError("Questionnaire answers are required!")

def get_client_questionnaire(user):

    session = SessionLocal()

    try:
        questionnaire = session.query(Questionnaire).filter(Questionnaire.client_id == user.id).first()
        if not questionnaire:
            raise ValueError("Questionnaire not found")

        return  questionnaire.to_dict()

    finally:
        session.close()

def update_questionnaire(answers, user):

     session = SessionLocal()

     try:
         questionnaire = session.query(Questionnaire).filter(Questionnaire.client_id == user.id).first()
         if not questionnaire:
            raise ValueError("Questionnaire not found")

         if datetime.utcnow() > questionnaire.editable_until:
             raise ValueError("Questionnaire can no longer be edited.")

         questionnaire.answers = answers

         session.commit()
         session.refresh(questionnaire)
         return questionnaire.to_dict()

     finally:
         session.close()

def get_questionnaire_by_client_id(client_id):

    session = SessionLocal()

    try:
        questionnaire = session.query(Questionnaire).filter(Questionnaire.client_id == client_id).first()
        if not questionnaire:
            raise ValueError("Questionnaire not found")
        return questionnaire.to_dict()

    finally:
        session.close()

def get_client_by_id(client_id, trainer_id):

    session = SessionLocal()

    try:
        client = (session.query(User).filter(User.id == client_id).filter(User.trainer_id == trainer_id).first())
        if not client:
            raise ValueError("Client not found")

        return client.to_dict()

    finally:
        session.close()


def create_plan(name, plan_type, client_id, trainer_id, daily_calories, daily_protein, daily_fat, daily_carbs, daily_water, coach_notes, start_date=None):
    session = SessionLocal()

    daily_calories = int(daily_calories) if daily_calories else None
    daily_protein = int(daily_protein) if daily_protein else None
    daily_carbs = int(daily_carbs) if daily_carbs else None
    daily_fat = int(daily_fat) if daily_fat else None
    daily_water = float(daily_water) if daily_water else None

    try:
        if not name.strip():
            raise ValueError("Plan name required")

        if plan_type not in ["calendar", "template"]:
            raise ValueError("Invalid plan type")

        if plan_type == "calendar" and not start_date:
            raise ValueError("Calendar plan type requires start_date")

        if plan_type == "template" and start_date:
            raise ValueError("Template plan cannot have start_date")

        if any(
                value is not None and value < 0
                for value in [
                    daily_calories,
                    daily_protein,
                    daily_carbs,
                    daily_fat,
                    daily_water,
                ]
        ):
            raise ValueError("The values should not be negative.")

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
            daily_calories=daily_calories,
            daily_protein=daily_protein,
            daily_fat=daily_fat,
            daily_carbs=daily_carbs,
            daily_water=daily_water,
            coach_notes=coach_notes
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

def get_plan_by_id(plan_id, user):
    session = SessionLocal()

    try:
        plan = session.get(Plan, plan_id)

        if not plan:
            return None

        if user.role == "trainer" and plan.trainer_id != user.id:
            return None

        if user.role == "client" and plan.client_id != user.id:
            return None

        return plan.to_dict()

    finally:
        session.close()


def delete_plan(plan_id, user):

    session = SessionLocal()

    try:
        plan = session.query(Plan).filter(Plan.id == plan_id).first()

        if not plan:
            raise ValueError("Plan not found")

        if user.role != "trainer":
            return None

        if user.role == "trainer" and plan.trainer_id != user.id:
            return None

        session.delete(plan)
        session.commit()

        return plan.to_dict()

    finally:
        session.close()

def update_plan(plan_id, name, plan_type, client_id, user, daily_calories, daily_protein, daily_carbs, daily_fat, daily_water, coach_notes, start_date=None):

    session = SessionLocal()

    try:
        plan = session.query(Plan).filter(Plan.id == plan_id).first()

        if not plan:
            raise ValueError("Plan not found")

        if not name.strip():
            raise ValueError("Plan name required")

        if user.role != "trainer":
            return None

        if user.role == "trainer" and plan.trainer_id != user.id:
            return None

        client = session.query(User).filter(User.id == client_id).first()

        if not client:
            raise ValueError("Client not found")

        if client.trainer_id != user.id:
            raise ValueError("Unauthorized client")

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
        plan.daily_calories = daily_calories
        plan.daily_protein = daily_protein
        plan.daily_carbs = daily_carbs
        plan.daily_fat = daily_fat
        plan.daily_water = daily_water
        plan.coach_notes = coach_notes

        session.commit()
        session.refresh(plan)

        return plan.to_dict()

    finally:
        session.close()


def create_meal(name, plan_id, day_number, user):

    session = SessionLocal()

    try:
        plan = session.query(Plan).filter(Plan.id == plan_id).first()

        if not plan:
            raise ValueError("Plan not found")

        if user.role != "trainer":
            return None

        if user.role == "trainer" and plan.trainer_id != user.id:
            return None

        if not name.strip():
            raise ValueError("Meal name required")

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

def get_meals_for_plan(plan_id, user):

    session = SessionLocal()

    try:
        plan = session.get(Plan, plan_id)

        if not plan:
            return []

        if user.role == "trainer" and plan.trainer_id != user.id:
            return None

        if user.role == "client" and plan.client_id != user.id:
            return None

        meals = [m.to_dict() for m in plan.meals]

        return meals

    finally:
        session.close()

def delete_meal(meal_id, user):

    session = SessionLocal()

    try:
        meal = session.query(Meal).filter(Meal.id == meal_id).first()

        if not meal:
            raise ValueError("Meal not found")

        if user.role != "trainer":
            return None

        if meal.plan.trainer_id != user.id:
            return None

        meal_data = meal.to_dict()

        session.delete(meal)
        session.commit()

        return meal_data

    finally:
        session.close()

def update_meal(meal_id, user, name):

    session = SessionLocal()

    try:
        meal = session.query(Meal).filter(Meal.id == meal_id).first()

        if not meal:
            raise ValueError("Food not found")

        if user.role != "trainer":
            return None

        meal.name = name

        session.commit()
        session.refresh(meal)

        return meal.to_dict()

    finally:
        session.close()

def get_clients_by_trainer(trainer_id):

    session = SessionLocal()

    try:
        clients = (session.query(User).filter(User.trainer_id == trainer_id).filter(User.role == "client").all())
        return [c.to_dict() for c in clients]

    finally:
        session.close()

def deactivate_client(client_id, trainer_id):

    session = SessionLocal()

    try:
        client = session.query(User).filter(User.id==client_id, User.trainer_id==trainer_id).first()

        if not client:
            raise ValueError("Client not found")

        client.is_active = False
        session.commit()
        session.refresh(client)

        return client.to_dict()

    finally:
        session.close()


def create_food_norm(user, name, calories, protein, carbs, fat):

    session = SessionLocal()

    try:
        if user.role != "trainer":
            return None

        name = name.strip()

        existing = session.query(FoodNorm).filter(FoodNorm.name == name, FoodNorm.created_by == user.id).first()

        if existing:
            raise ValueError("Food already exists.")

        if any(float(value or 0) < 0 for value in [calories, protein, fat, carbs]):
            raise ValueError("Values cannot be negative")

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

def delete_food_norm(food_id, user):

    session = SessionLocal()

    try:
        if user.role != "trainer":
            return None

        food_norm = session.query(FoodNorm).filter(FoodNorm.id == food_id, FoodNorm.created_by == user.id).first()

        if not food_norm:
            raise ValueError("Food not found")

        food_data = food_norm.to_dict()

        session.delete(food_norm)
        session.commit()

        return food_data

    finally:
        session.close()



def create_food(meal_id, food_norm_id, grams, user):

    session = SessionLocal()

    try:
        meal = session.query(Meal).filter(Meal.id == meal_id).first()
        if not meal:
            raise ValueError("Meal not found")

        if user.role != "trainer":
            return None

        if meal.plan.trainer_id != user.id:
            return None

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

def delete_food(food_id, user):

    session = SessionLocal()

    try:
        food = session.query(Food).filter(Food.id == food_id).first()

        if not food:
            raise ValueError("Food not found")

        if user.role != "trainer":
            return None

        if food.meal.plan.trainer_id != user.id:
            return None

        meal = food.meal

        session.delete(food)
        session.commit()

        return meal.to_dict()
    finally:
        session.close()

def update_food(food_id, grams, user):
    session = SessionLocal()

    try:
        food = session.query(Food).filter(Food.id == food_id).first()

        if not food:
            raise ValueError("Food not found")

        if user.role != "trainer":
            return None

        if food.meal.plan.trainer_id != user.id:
            return None

        grams = float(grams)
        if grams <= 0:
            raise ValueError("Grams must be positive")

        food.grams = grams

        session.commit()
        session.refresh(food)

        result = food.meal.to_dict()
        return result

    finally:
        session.close()