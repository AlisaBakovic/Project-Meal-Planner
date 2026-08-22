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
    get_food_norms,
    delete_food,
    update_food,
    delete_meal,
    get_client_by_id,
    create_invite,
    validate_invite_token,
    accept_invite,
    revoke_invitation,
    get_invitation,
    deactivate_client, delete_food_norm, create_questionnaire, get_client_questionnaire, update_questionnaire,
    get_questionnaire_by_client_id, resend_invitation, update_meal,
)
from auth import get_current_user
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL")

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

Base.metadata.create_all(engine)

@app.route("/", methods=["GET"])
def hello_route():
    return jsonify({"Message": "Hello from backend"}), 200


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
        token, user = login_user(
            email=data["email"],
            password=data["password"]
        )

        return jsonify({
            "token": token,
            "first_name": user.first_name,
            "role": user.role
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/invites", methods=["POST"])
def invite_route():

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    data = request.json

    if not data:
        return jsonify({"error": "Missing data"}), 400

    try:
        invite = create_invite(
            email=data["email"],
            trainer_id=user.id
        )

        return jsonify(invite), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/invites/<token>", methods=["GET"])
def validate_token_route(token):

    try:
        validate_token = validate_invite_token(token=token)

        return jsonify(validate_token), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/accept-invite", methods=["POST"])
def accept_invite_route():

    data = request.json

    try:
        accept_invitation = accept_invite(
            token=data["token"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            password=data["password"]
        )

        return jsonify(accept_invitation), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/invites/<int:invite_id>/revoke", methods=["PATCH"])
def revoke_invitation_route(invite_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    try:
        revoke_invitation(invite_id, user.id)
        return jsonify({"message": "Invitation revoked"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/invites/<int:invite_id>/resend", methods=["PATCH"])
def resend_invitation_route(invite_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    try:
        invite = resend_invitation(invite_id, user.id)
        return jsonify(invite), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/invites", methods=["GET"])
def get_invitations_route():

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    invitations = get_invitation(user.id)

    return jsonify(invitations)

@app.route("/questionnaire", methods=["POST"])
def create_questionnaire_route():

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "client":
        return jsonify({"error": "Forbidden"}), 403

    data = request.json

    try:
        questionnaire = create_questionnaire(
            answers=data.get("answers"),
            user=user,
        )

        return  jsonify(questionnaire), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/questionnaire", methods=["GET"])
def get_questionnaire_route():
    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "client":
        return jsonify({"error": "Forbidden"}), 403

    questionnaire = get_client_questionnaire(user)

    return jsonify(questionnaire)

@app.route("/questionnaire", methods=["PUT"])
def update_questionnaire_route():
    user = get_current_user()

    if user.role != "client":
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    try:
        questionnaire = update_questionnaire(data["answers"], user)

        return jsonify(questionnaire), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/trainer/questionnaire/<int:client_id>", methods=["GET"])
def get_questionnaire_by_client_id_route(client_id):

    user = get_current_user()

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    try:
        questionnaire = get_questionnaire_by_client_id(client_id)

        return jsonify(questionnaire), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route("/plans", methods=["POST"])
def create_plan_route():

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    data = request.json

    try:
        plan = create_plan(
            name=data["name"],
            plan_type=data["plan_type"],
            start_date=data.get("start_date"),
            client_id=data["client_id"],
            trainer_id=user.id,
            daily_calories=data["daily_calories"],
            daily_protein=data["daily_protein"],
            daily_fat=data["daily_fat"],
            daily_carbs=data["daily_carbs"],
            daily_water=data["daily_water"],
            coach_notes=data["coach_notes"]
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

    plan = get_plan_by_id(plan_id, user)

    if not plan:
        return jsonify({"error": "Plan not found"}), 404

    return jsonify(plan)


@app.route("/plans/<int:plan_id>", methods=["DELETE"])
def delete_plan_by_id(plan_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    try:
        delete_plan(plan_id, user)

        return jsonify({"message": "Plan deleted"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@app.route("/plans/<int:plan_id>", methods=["PUT"])
def update_plan_by_id(plan_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    data = request.json

    try:
        plan = update_plan(
            plan_id=plan_id,
            name=data["name"],
            plan_type=data["plan_type"],
            start_date=data.get("start_date"),
            client_id=data["client_id"],
            user=user,
            daily_calories = data["daily_calories"],
            daily_protein = data["daily_protein"],
            daily_carbs = data["daily_carbs"],
            daily_fat = data["daily_fat"],
            daily_water = data["daily_water"],
            coach_notes = data["coach_notes"]
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
            name=data["name"],
            plan_id=plan_id,
            day_number=data["day_number"],
            user=user
        )

        return jsonify(meal), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/meals/<int:meal_id>", methods=["DELETE"])
def delete_meal_route(meal_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        delete_meal(meal_id, user)

        return jsonify({"message": "Meal deleted"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
@app.route("/meals/<int:meal_id>", methods=["PUT"])
def update_meal_route(meal_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    try:
        meal = update_meal(
            user=user,
            meal_id=meal_id,
            name=data["name"]
        )

        return jsonify(meal), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/plans/<int:plan_id>/meals", methods=["GET"])
def get_meals_by_plan_id(plan_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    meals = get_meals_for_plan(plan_id, user)

    return jsonify(meals)


@app.route("/clients", methods=["GET"])
def get_clients():

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    clients = get_clients_by_trainer(user.id)

    return jsonify(clients)


@app.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        client = get_client_by_id(client_id, user.id)

        return jsonify(client), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route("/clients/<int:client_id>/deactivate", methods=["PATCH"])
def deactivate_client_route(client_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    client = deactivate_client(client_id, user.id)

    return jsonify(client), 200


@app.route("/meals/<int:meal_id>/foods", methods=["POST"])
def add_food_to_meal(meal_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    try:
        food = create_food(
            meal_id=meal_id,
            food_norm_id=data["food_norm_id"],
            grams=data["grams"],
            user=user
        )

        return jsonify(food), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/foods", methods=["POST"])
def create_food_norm_route():

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

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

@app.route("/foods/<int:food_id>", methods=["DELETE"])
def delete_food_norm_route(food_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    try:
        delete_food_norm(food_id, user)

        return jsonify({"message": "Food deleted"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

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

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    try:
        delete_food(food_id, user)

        return jsonify({"message": "Food deleted"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@app.route("/foods/<int:food_id>", methods=["PUT"])
def update_food_route(food_id):

    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user.role != "trainer":
        return jsonify({"error": "Forbidden"}), 403

    data = request.json

    if not data:
        return jsonify({"error": "Missing data"}), 400

    if data.get("grams") is None:
        return jsonify({"error": "Grams is required"}), 400

    try:
        food = update_food(
            food_id=food_id,
            grams=data.get("grams"),
            user=user
        )

        return jsonify(food), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)