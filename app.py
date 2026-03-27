from flask import Flask, request, jsonify, session
from database import engine, Base, SessionLocal
from models import User
from services import (
    create_meal,
    get_plans,
    create_plan,
    get_meals_for_plan,
    get_plan_by_id,
    login_user,
)
from auth import decode_token, get_current_user
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

Base.metadata.create_all(engine)


@app.route("/login", methods=["POST"])
def login_route():
    data = request.json

    if not data:
        return jsonify({"Missing data"}), 400

    try:
        token = login_user(email=data["email"], password=data["password"])
        return jsonify({"token": token}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/plans", methods=["POST"])
def create_plan_route():

    user = get_current_user()

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json

    try:
        plan = create_plan(
            name=data["name"],
            plan_type=data["plan_type"],
            start_date=data.get("start_date"),
            client_id=data["client_id"],
            trainer_id=user.id,
        )
        return jsonify(plan.to_dict()), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/plans", methods=["GET"])
def get_plans_route():

    user = get_current_user()
    plans = get_plans(user)
    return jsonify([p.to_dict() for p in plans])


@app.route("/plans/<int:plan_id>", methods=["GET"])
def get_plans_by_id(plan_id):
    plan = get_plan_by_id(plan_id)

    if not plan:
        return jsonify({"error": "Plan not found"}, 404)
    return jsonify(plan.to_dict())


@app.route("/plans/<int:plan_id>/meals", methods=["POST"])
def create_meal_route(plan_id):
    data = request.json

    try:
        meal = create_meal(
            name=data["name"], plan_id=plan_id, day_number=data["day_number"]
        )
        return jsonify(meal.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/plans/<int:plan_id>/meals", methods=["GET"])
def get_meals_by_plan_id(plan_id):
    meals = get_meals_for_plan(plan_id)

    return jsonify([m.to_dict() for m in meals])


if __name__ == "__main__":
    app.run(debug=True)
