from flask import Flask, request, jsonify
from database import engine, Base
import models
from services import create_meal, get_plans, create_plan, get_meals_for_plan, get_plan_by_id

app = Flask(__name__)

Base.metadata.create_all(engine)

@app.route("/plans", methods=["POST"])
def create_plan_route():
    data = request.json

    try:
        plan = create_plan(
            name=data["name"],
            plan_type=data["plan_type"],
            start_date=data.get("start_date")
        )
        return jsonify(plan.to_dict()), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/plans", methods=["GET"])
def get_plans_route():
    plans = get_plans()
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
            name=data["name"],
            plan_id=plan_id,
            day_number=data["day_number"]
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


