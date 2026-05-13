from pathlib import Path
import csv

from pymongo import MongoClient


def load_predictions(pred_path: Path) -> list[dict[str, str]]:
    predictions = []
    if pred_path.exists():
        with pred_path.open("r", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                predictions.append(row)
    return predictions


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    pred_path = project_root / "output" / "next_month_prediction.csv"

    client = MongoClient("mongodb://localhost:27017/")
    db = client["energy_predictions"]

    predictions = load_predictions(pred_path)
    if predictions:
        db.predictions.insert_many(predictions)
        print(f"Inserted {len(predictions)} predictions into MongoDB")
    else:
        db.predictions.insert_one(
            {"message": "Sample prediction data", "status": "processed"}
        )
        print("Inserted sample data into MongoDB")

    client.close()


if __name__ == "__main__":
    main()
