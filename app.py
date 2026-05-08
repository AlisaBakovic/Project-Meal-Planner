from flask import Flask, request, jsonify
from database import engine, Base
from services import (
    create_meal,
    get_plans,
    create_plan,
    get_meals_for_plan,
    get_plan_by_id,
    login_user,
    get_clients_by_trainer,
    delete_plan,
    update_plan,
    register_trainer,
    create_food,
    create_food_norm,
    get_food_norms, delete_food, update_food, delete_meal,
)
from auth import decode_token, get_current_user
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

Base.metadata.create_all(engine)

@app.route("/register", methods=["POST"])
def register_route():

    data = request.json

    if not data:
        return jsonify({"error": "Missing data"}), 400

    try:
        user = register_trainer(
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

        return jsonify(user), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/login", methods=["POST"])
def login_route():

    data = request.json

    if not data:
        return jsonify({"error": "Missing data"}), 400

    try:
        token = login_user(email=data["email"], password=data["password"])
        return jsonify({"token": token}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/plans", methods=["POST"])
def create_plan_route():

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    try:
        plan = create_plan(
            name=data["name"],
            plan_type=data["plan_type"],
            start_date=data.get("start_date"),
            client_id=data["client_id"],
            trainer_id=user.id,
        )
        return jsonify(plan), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/plans", methods=["GET"])
def get_plans_route():

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    plans = get_plans(user)
    return jsonify(plans)


@app.route("/plans/<int:plan_id>", methods=["GET"])
def get_plans_by_id(plan_id):

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    plan = get_plan_by_id(plan_id)

    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    return jsonify(plan)


@app.route("/plans/<int:plan_id>", methods=["DELETE"])
def delete_plan_by_id(plan_id):

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        delete_plan(plan_id)
        return jsonify({"message": "Plan deleted"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@app.route("/plans/<int:plan_id>", methods=["PUT"])
def update_plan_by_id(plan_id):

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    try:
        plan = update_plan(
            plan_id=plan_id,
            name=data["name"],
            plan_type=data["plan_type"],
            start_date=data.get("start_date"),
            client_id=data["client_id"],
        )
        return jsonify(plan), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@app.route("/plans/<int:plan_id>/meals", methods=["POST"])
def create_meal_route(plan_id):

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    try:
        meal = create_meal(
            name=data["name"], plan_id=plan_id, day_number=data["day_number"]
        )
        return jsonify(meal), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/meals/<int:meal_id>", methods=["DELETE"])
def delete_meal_route(meal_id):

    try:
        user = get_current_user()
    except Exception:
        return jsonify({"error": "Unauthorized"}), 401

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        delete_meal(meal_id)
        return jsonify({"message": "Meal deleted"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/plans/<int:plan_id>/meals", methods=["GET"])
def get_meals_by_plan_id(plan_id):

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    meals = get_meals_for_plan(plan_id)

    return jsonify(meals)

@app.route("/clients", methods=["GET"])
def get_clients():

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    clients = get_clients_by_trainer(user.id)

    return jsonify(clients)


@app.route("/meals/<int:meal_id>/foods", methods=["POST"])
def add_food_to_meal(meal_id):

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    try:
        food = create_food(
            meal_id=meal_id, food_norm_id=data["food_norm_id"], grams=data["grams"]
        )

        return jsonify(food), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/foods", methods=["POST"])
def create_food_norm_route():

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    if not data:
        return jsonify({"error": "Missing data"}), 400

    try:
        food = create_food_norm(
            user=user,
            name=data["name"],
            calories=data["calories"],
            protein=data["protein"],
            carbs=data["carbs"],
            fat=data["fat"],
        )
        return jsonify(food), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/foods", methods=["GET"])
def get_foods_route():

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    foods = get_food_norms(user)

    return jsonify(foods)

@app.route("/foods/<int:food_id>", methods=["DELETE"])
def delete_food_route(food_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        delete_food(food_id)

        return jsonify({"message": "Food deleted"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/foods/<int:food_id>", methods=["PUT"])
def update_food_route(food_id):

    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    if not data:
        return jsonify({"error": "Missing data"}), 400

    if data.get("grams") is None:
        return jsonify({"error": "Grams is required"}), 400

    try:
        food = update_food(food_id=food_id, grams=data.get("grams"))
        return jsonify(food), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
