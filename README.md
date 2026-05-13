# BDA Project - Energy Consumption Prediction

A Big Data Analytics project for predicting energy consumption using Hadoop and Machine Learning.

## Project Overview

This project implements a complete Big Data pipeline for analyzing and predicting household energy consumption using:
- **Hadoop HDFS** for distributed storage
- **MapReduce** for parallel data processing
- **Machine Learning** (Linear Regression, Random Forest) for prediction
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
│   ├── preprocessing/        # Data cleaning and feature engineering
│   ├── ml/                   # Machine learning models
│   ├── visualization/        # Data visualization scripts
│   ├── notebooks/            # Jupyter notebooks
│   ├── output/               # Processed data and predictions
│   ├── requirements.txt      # Python dependencies
│   ├── main.py               # Main execution script
│   ├── docker-compose.yml    # Docker Hadoop setup
│   └── README.md             # Detailed project README
│
└── venv/                     # Python virtual environment (not tracked in git)
```

## Quick Start

### Prerequisites
- Python 3.8+
- Docker Desktop (for Hadoop)
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

Run the complete pipeline:
The large dataset file was excluded from the repo. To use the project, download the dataset from https://archive.ics.uci.edu/ml/datasets/
```bash
python energy-consumption-prediction/main.py
```

Or run individual components:
```bash
# Preprocessing
python energy-consumption-prediction/preprocessing/preprocess_pipeline.py

# Train models
python energy-consumption-prediction/ml/train_linear_regression.py
python energy-consumption-prediction/ml/train_random_forest.py

# Evaluate
python energy-consumption-prediction/ml/evaluate_model.py

# Visualize
python energy-consumption-prediction/visualization/visualization.py
```

## Documentation

- Detailed project documentation: [Docs/enhanced_energy_consumption_prediction_hadoop_ml_report.md](Docs/enhanced_energy_consumption_prediction_hadoop_ml_report.md)
- Project-specific README: [energy-consumption-prediction/README.md](energy-consumption-prediction/README.md)

## Technologies Used

- **Big Data**: Hadoop HDFS, MapReduce, Spark
- **Machine Learning**: scikit-learn, pandas, numpy
- **Visualization**: matplotlib, seaborn, plotly
- **Dashboard**: Streamlit
- **Containerization**: Docker

## License

For academic and demonstration purposes.

