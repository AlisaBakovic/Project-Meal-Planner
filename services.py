from datetime import datetime

from flask import session

from database import SessionLocal
from models import Plan, Meal

def create_plan(name, plan_type, start_date=None):
    session = SessionLocal()

    if plan_type not in ["calendar","template"]:
        raise ValueError("Invalid plan type")

    if plan_type == "calendar" and not start_date:
        raise ValueError("Calendar plan type requires start_date")

    if plan_type == "template" and start_date:
        raise ValueError("Template plan cannot have start_date")

    if start_date:
        start_date = datetime.fromisoformat(start_date).date()

    plan = Plan(name=name, plan_type=plan_type, start_date=start_date)

    session.add(plan)
    session.commit()

    return plan

def get_plans():

    session = SessionLocal()
    plans = session.query(Plan).all()
    return plans

def get_plan_by_id(plan_id):

    session = SessionLocal()
    plan = session.get(Plan, plan_id)
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
