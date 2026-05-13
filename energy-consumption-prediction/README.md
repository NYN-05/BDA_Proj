# Energy Consumption Prediction Using Hadoop and Machine Learning

A complete, beginner-friendly Big Data + Machine Learning pipeline that processes the UCI Individual Household Electric Power Consumption dataset using Hadoop MapReduce and trains predictive ML models in Python.

## Project Overview
This project demonstrates:
- Distributed storage and preprocessing using Hadoop HDFS and MapReduce
- Time-series forecasting using Spark MLlib
- Prediction storage in MongoDB (local)
- Visualization and reporting

## Architecture
```
Raw dataset -> HDFS -> MapReduce (hourly aggregation) ->
Local preprocessing (monthly features) -> ML training -> Next-month forecast
```

## Features
- Windows 11 compatible scripts and setup steps
- Dockerized Hadoop (HDFS + MapReduce)
- Reproducible preprocessing and model training
- Clear outputs saved to the output/ folder

## Folder Structure
```
energy-consumption-prediction/
│
├── dataset/
│   └── household_power_consumption.txt
│
├── hadoop/
│   ├── mapper.py
│   ├── reducer.py
│   ├── run_mapreduce.bat
│   ├── upload_to_hdfs.bat
│   └── hadoop_commands.md
│
├── preprocessing/
│   ├── clean_data.py
│   └── feature_engineering.py
│
├── ml/
│   └── saved_models/
│
├── visualization/
│   └── charts/
│

│
├── notebooks/
│   └── experimentation.ipynb
│
├── output/
│   ├── processed_data.csv
│   ├── predictions.csv
│   └── metrics.txt
│
├── requirements.txt
├── README.md
├── .gitignore
└── main.py
```

## Windows 11 Setup (Docker Hadoop)

### 1) Install Docker Desktop
- Install Docker Desktop and enable WSL2 backend.
- Ensure `docker` and `docker compose` work in PowerShell.

### 2) Start Hadoop in Docker
From the project root:
```bat
docker compose up -d
```

### 3) (One-Time) Install Python in the Hadoop Container
The streaming job runs `python3` inside the Hadoop container.
```bat
cd hadoop
docker_install_python.bat
```

## Python Setup
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Project

### 1) Run Spark MLlib Forecast (after MapReduce)
```bat
python main.py
```

### 2) Run MapReduce on Docker Hadoop
```bat
cd hadoop
upload_to_hdfs.bat
run_mapreduce.bat
```
MapReduce output is saved to output/mapreduce_hourly_avg.csv.

### 3) Store Spark Predictions in MongoDB
```bat
python scripts\store_spark_predictions.py
```

### 4) Hive Trend Analysis (Optional)
Hive runs inside the Hadoop docker stack if the hive-server container is available.
```bat
docker exec -i hive-server hive -f /workspace/hadoop/hive_trend_analysis.hql
```

### 4) running the server-backend & fronted:
```bat
The project has:
- Backend: FastAPI in api/app.py
- Frontend: HTML in ui/index.html
To run them:
Terminal 1 - Backend:
cd C:\Users\JHASHANK\Downloads\BDA_PROJ\energy-consumption-prediction
.\venv\Scripts\python.exe -m uvicorn api.app:app --reload --port 8000
Terminal 2 - Frontend (optional):
The frontend is just a static HTML file. Open ui/index.html directly in browser, or serve it:
cd C:\Users\JHASHANK\Downloads\BDA_PROJ\energy-consumption-prediction\ui
python -m http.server 3000
Then open http://localhost:3000
```

## Local MongoDB (no Docker)
This project expects MongoDB to be installed locally and running on:

```
mongodb://localhost:27017/
```

The API will store predictions in the `energy_predictions.predictions` collection.
You can override the connection with environment variables:

```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=energy_predictions
MONGODB_COLLECTION=predictions
```


## Outputs
- output/processed_monthly.csv
- output/next_month_prediction.csv
- output/metrics.txt
- visualization/charts/*.png

## Prediction Schema
All Spark predictions follow a single schema across CSV, MongoDB, and API responses:

```json
{
	"schema_version": "1.0",
	"date_hour": "YYYY-MM-DD HH",
	"avg_power": 1.2345,
	"predicted_power": 1.3456,
	"model": "spark_mllib",
	"source": "spark_local",
	"generated_at": "YYYY-MM-DDTHH:MM:SSZ"
}
```

## API Endpoints
- `GET /db/health`: MongoDB connectivity check
- `GET /predictions/latest`: latest stored prediction
- `POST /predict`: store latest Spark forecast and return it

## Screenshots (Placeholders)
- dashboard screenshot
- prediction charts
- MapReduce output

## Troubleshooting
- If MapReduce fails, re-run `hadoop\docker_install_python.bat`.
- If scripts fail in PowerShell, try CMD.
- Ensure dataset file is at dataset/household_power_consumption.txt.

## Validation
To validate prediction consistency and MongoDB storage:

```bat
python scripts\validate_prediction_consistency.py
```

## License
Use for academic and demonstration purposes.
