from database import SessionLocal
from models import FoodNorm
from seed_data import foods


def seed_foods():

    session = SessionLocal()

    for f in foods:
        name = f["name"].strip().lower()
        existing = session.query(FoodNorm).filter(FoodNorm.name == name).first()

        if existing:
            continue

        food = FoodNorm(
            name=name,
            created_by=None,
            calories_per_g=float(f["calories"]) / 100,
            protein_per_g=float(f["protein"]) / 100,
            fat_per_g=float(f["fat"]) / 100,
            carbs_per_g=float(f["carbs"]) / 100,
        )

        session.add(food)

    session.commit()
    session.close()


if __name__ == "__main__":
    seed_foods()
