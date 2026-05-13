# BDA Project - Energy Consumption Prediction

A Big Data Analytics project for predicting energy consumption using Hadoop and Machine Learning.

## Project Overview

This project implements a complete Big Data pipeline for analyzing and predicting household energy consumption using:
- **Hadoop HDFS** for distributed storage
- **MapReduce** for parallel data processing
- **Spark MLlib** for forecasting
- **MongoDB** for prediction storage
- **Visualization** for results presentation

## Repository Structure

```
BDA_PROJ/
├── Docs/
│   └── enhanced_energy_consumption_prediction_hadoop_ml_report.md
│
├── energy-consumption-prediction/
│   ├── dataset/              # Raw dataset (UCI Individual Household Electric Power Consumption)
│   ├── hadoop/               # Hadoop MapReduce scripts
│   ├── preprocessing/        # Data cleaning helpers
│   ├── ml/                   # Spark model artifacts (optional)
│   ├── visualization/        # Charts output (optional)
│   ├── notebooks/            # Jupyter notebooks
│   ├── output/               # Processed data and predictions
│   ├── requirements.txt      # Python dependencies
│   ├── main.py               # Main execution script
│   └── README.md             # Detailed project README
│
└── venv/                     # Python virtual environment (not tracked in git)
```

## Quick Start

### Prerequisites
- Python 3.8+
- Docker Desktop (for Hadoop)
- MongoDB (local instance)
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/NYN-05/BDA_PROJECT.git
cd BDA_PROJECT
```

2. Set up Python virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r energy-consumption-prediction/requirements.txt
```

3. Start Hadoop (Docker):
```bash
cd energy-consumption-prediction
docker compose up -d
```

### Running the Project

Run the Spark MLlib forecast (after MapReduce output exists):
The large dataset file was excluded from the repo. To use the project, download the dataset from https://archive.ics.uci.edu/ml/datasets/
```bash
python energy-consumption-prediction/main.py
```

Store the latest Spark forecast in MongoDB:
```bash
python energy-consumption-prediction/scripts/store_spark_predictions.py
```

## Documentation

- Detailed project documentation: [Docs/enhanced_energy_consumption_prediction_hadoop_ml_report.md](Docs/enhanced_energy_consumption_prediction_hadoop_ml_report.md)
- Project-specific README: [energy-consumption-prediction/README.md](energy-consumption-prediction/README.md)

## Technologies Used

- **Big Data**: Hadoop HDFS, MapReduce, Spark
- **Machine Learning**: Spark MLlib, pandas, numpy
- **Visualization**: matplotlib, seaborn, plotly
- **Dashboard**: Streamlit
- **Database**: MongoDB (local)

## License

For academic and demonstration purposes.

