
from pymongo import MongoClient
import csv
import os

client = MongoClient('mongodb://mongo:27017/')
db = client['energy_predictions']

predictions = []
pred_path = '/workspace/output/next_month_prediction.csv'
if os.path.exists(pred_path):
    with open(pred_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            predictions.append(row)
    
    if predictions:
        db.predictions.insert_many(predictions)
        print(f"Inserted {len(predictions)} predictions into MongoDB")
else:
    db.predictions.insert_one({"message": "Sample prediction data", "status": "processed"})
    print("Inserted sample data into MongoDB")

client.close()
