from datetime import datetime

from flask import session
from sqlalchemy.cyextension.processors import str_to_date
from sqlalchemy.testing.suite.test_reflection import users
from werkzeug.security import generate_password_hash, check_password_hash

from auth import generate_token
from database import SessionLocal
from models import Plan, Meal, User


def register_trainer(email, password, first_name, last_name):
    session = SessionLocal()

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

    return user


def login_user(email, password):

    session = SessionLocal()

    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Invalid email or password")

    if not check_password_hash(user.password_hash, password):
        raise ValueError("Invalid email or password")

    token = generate_token(user)

    return token


def create_plan(name, plan_type, client_id, trainer_id, start_date=None):
    session = SessionLocal()

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

    return plan


def get_plans(user):

    session = SessionLocal()

    if user.role == "trainer":
        plans = session.query(Plan).filter(Plan.trainer_id == user.id).all()
    elif user.role == "client":
        plans = session.query(Plan).filter(Plan.client_id == user.id).all()
    else:
        raise ValueError("Undefined user")
    return plans


def get_plan_by_id(plan_id):

    session = SessionLocal()
    plan = session.get(Plan, plan_id)
    return plan


def delete_plan(plan_id):

    session = SessionLocal()

    plan = session.query(Plan).filter(Plan.id == plan_id).first()

    if not plan:
        raise ValueError("Plan not found")
    session.delete(plan)
    session.commit()

    return plan


def update_plan(plan_id, name, plan_type, client_id, start_date=None):

    session = SessionLocal()

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

    return plan


def create_meal(name, plan_id, day_number):

    session = SessionLocal()
    meal = Meal(name=name, plan_id=plan_id, day_number=day_number)
    session.add(meal)
    session.commit()

    return meal


def get_meals_for_plan(plan_id):

    session = SessionLocal()
    plan = session.get(Plan, plan_id)

    if not plan:
        return None

    return plan.meals


def get_clients_by_trainer(trainer_id):

    session = SessionLocal()

    clients = (
        session.query(User)
        .filter(User.trainer_id == trainer_id)
        .filter(User.role == "client")
        .all()
    )

    return clients
