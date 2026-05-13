# ENERGY CONSUMPTION PREDICTION USING HADOOP AND MACHINE LEARNING

---

# PROJECT REPORT

## ENERGY CONSUMPTION PREDICTION USING HADOOP, BIG DATA ANALYTICS, AND MACHINE LEARNING

---

# ABSTRACT

Energy consumption forecasting is one of the most important applications in modern smart grids, industries, power systems, and urban infrastructure. Accurate prediction of electricity usage helps optimize power generation, reduce energy wastage, improve operational efficiency, and support intelligent decision-making.

Traditional systems struggle when dealing with massive energy datasets generated from smart meters, IoT devices, sensors, and distributed monitoring systems. These datasets are extremely large, continuously growing, and require scalable distributed processing.

This project presents a scalable Energy Consumption Prediction System using Hadoop and Machine Learning. Hadoop Distributed File System (HDFS) is used for distributed storage, while MapReduce is used for large-scale preprocessing and parallel data handling. After preprocessing, Machine Learning algorithms are applied to predict future energy consumption patterns.

The project combines Big Data technologies with predictive analytics to build a fault-tolerant, scalable, and efficient forecasting platform.

---

# TABLE OF CONTENTS

1. Introduction
2. Problem Statement
3. Objectives
4. Existing System
5. Proposed System
6. Technology Stack
7. System Architecture
8. Workflow
9. Dataset Description
10. Methodology
11. Hadoop Implementation
12. Machine Learning Models
13. Code Snippets
14. Results and Analysis
15. Advantages
16. Limitations
17. Future Enhancements
18. Conclusion
19. References

---

# 1. INTRODUCTION

The demand for electricity is increasing rapidly because of industrialization, urbanization, smart cities, and the growing usage of IoT-based devices. Efficient energy management has become a critical requirement for governments, industries, and utility providers.

Energy consumption forecasting helps:

- Predict future electricity demand
- Prevent overloading in power grids
- Reduce operational costs
- Improve resource allocation
- Enable intelligent smart grid management

Modern energy systems generate huge volumes of data every second. Traditional databases and standalone systems are not efficient enough to process such large-scale datasets.

To solve this problem, this project integrates:

- Hadoop for distributed storage and processing
- MapReduce for parallel preprocessing
- Machine Learning for prediction and forecasting

The complete system is capable of handling large datasets efficiently while providing accurate prediction results.

---

# 2. PROBLEM STATEMENT

Traditional energy monitoring systems face several major challenges:

## Problems in Existing Systems

### 1. Scalability Issues

Traditional systems cannot efficiently process terabytes of energy data.

### 2. Slow Processing

Sequential processing becomes inefficient for large datasets.

### 3. Poor Prediction Accuracy

Basic statistical methods fail to provide accurate forecasting.

### 4. Lack of Distributed Processing

Most traditional systems cannot utilize distributed computing.

### 5. Fault Tolerance Problems

Failure of a single system can affect the entire process.

---

# 3. OBJECTIVES

## Primary Objectives

- Build a distributed storage system using Hadoop HDFS
- Process large datasets using MapReduce
- Train machine learning models for prediction
- Predict future energy consumption accurately
- Analyze energy usage patterns

## Secondary Objectives

- Improve scalability
- Ensure fault tolerance
- Reduce processing time
- Understand Big Data analytics
- Integrate Hadoop with Machine Learning

---

# 4. EXISTING SYSTEM

In traditional systems:

- Data is stored in centralized databases
- Processing is performed sequentially
- Systems fail under large workloads
- Prediction models are less accurate
- Real-time scalability is limited

## Disadvantages of Existing System

| Problem | Description |
|---|---|
| Storage Limitation | Difficult to handle massive datasets |
| Processing Delay | Sequential execution is slow |
| Low Scalability | Cannot scale dynamically |
| Limited Fault Tolerance | Failure affects complete system |
| High Computational Cost | Large systems require expensive hardware |

---

# 5. PROPOSED SYSTEM

The proposed system uses Hadoop and Machine Learning for scalable energy prediction.

## Key Features

- Distributed data storage using HDFS
- Parallel processing using MapReduce
- Data preprocessing pipeline
- Feature engineering
- ML-based prediction models
- Fault-tolerant architecture

## Proposed Solution Flow

1. Collect energy data
2. Store data in HDFS
3. Process data using MapReduce
4. Clean and transform data
5. Train ML model
6. Predict future consumption
7. Visualize prediction results

---

# 6. TECHNOLOGY STACK

## Big Data Technologies

| Technology | Purpose |
|---|---|
| Hadoop HDFS | Distributed storage |
| Hadoop MapReduce | Parallel data processing |
| YARN | Resource management |
| Apache Hadoop | Big Data ecosystem |

## Machine Learning Technologies

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Scikit-learn | Machine learning library |
| Pandas | Data analysis |
| NumPy | Numerical computation |
| Matplotlib | Visualization |

## Development Tools

| Tool | Purpose |
|---|---|
| Jupyter Notebook | Model development |
| VS Code | Code editor |
| Linux Terminal | Hadoop execution |
| Git | Version control |

## Programming Languages Used

- Python
- Java (for Hadoop environment)
- Shell Scripting

---

# 7. SYSTEM ARCHITECTURE

## Overall Architecture

```text
                    +----------------+
                    |  Data Source   |
                    | Smart Meters   |
                    +----------------+
                             |
                             v
                    +----------------+
                    |     HDFS       |
                    | Distributed    |
                    | Storage Layer  |
                    +----------------+
                             |
                             v
                    +----------------+
                    |  MapReduce     |
                    | Preprocessing  |
                    +----------------+
                             |
                             v
                    +----------------+
                    | Feature        |
                    | Engineering    |
                    +----------------+
                             |
                             v
                    +----------------+
                    | Machine        |
                    | Learning       |
                    +----------------+
                             |
                             v
                    +----------------+
                    | Prediction     |
                    | Output         |
                    +----------------+
```

---

# 8. WORKFLOW

## Step-by-Step Workflow

### Step 1: Data Collection

Energy consumption datasets are collected from public repositories.

### Step 2: Data Storage

The dataset is uploaded into Hadoop Distributed File System (HDFS).

### Step 3: Data Processing

MapReduce jobs preprocess the raw dataset.

### Step 4: Data Cleaning

- Remove missing values
- Remove invalid records
- Handle outliers
- Normalize features

### Step 5: Feature Engineering

Extract useful features such as:

- Hour
- Day
- Month
- Voltage trends
- Power consumption patterns

### Step 6: Machine Learning

Train regression models on processed data.

### Step 7: Prediction

Predict future energy consumption.

### Step 8: Result Visualization

Display graphs and performance metrics.

---

# 9. DATASET DESCRIPTION

## Dataset Used

### UCI Individual Household Electric Power Consumption Dataset

The dataset contains household electrical measurements collected over time.

## Dataset Features

| Attribute | Description |
|---|---|
| Date | Date of recording |
| Time | Time of recording |
| Global_active_power | Household active power |
| Global_reactive_power | Reactive power |
| Voltage | Voltage measurement |
| Global_intensity | Current intensity |
| Sub_metering_1 | Kitchen energy usage |
| Sub_metering_2 | Laundry energy usage |
| Sub_metering_3 | Water heater and AC usage |

## Dataset Characteristics

- Time-series dataset
- Large volume of records
- Real-world electricity consumption data
- Suitable for forecasting applications

---

# 10. METHODOLOGY

## 10.1 Data Ingestion

Dataset is uploaded to HDFS.

## Hadoop Command

```bash
hdfs dfs -mkdir /input
hdfs dfs -put household_power_consumption.txt /input/
```

---

## 10.2 Data Preprocessing using MapReduce

### Mapper Function

The mapper reads raw records and emits key-value pairs.

### Reducer Function

The reducer aggregates data and removes invalid records.

---

## 10.3 Data Cleaning

Techniques used:

- Missing value handling
- Duplicate removal
- Noise reduction
- Data normalization

---

## 10.4 Feature Engineering

Extracted Features:

| Feature | Purpose |
|---|---|
| Hour | Peak usage detection |
| Day | Weekly trend analysis |
| Month | Seasonal pattern analysis |
| Voltage | Electrical behavior analysis |

---

## 10.5 Model Training

Machine learning models used:

### 1. Linear Regression

Used as a baseline model.

### 2. Random Forest Regressor

Used for improved prediction accuracy.

---

## 10.6 Model Evaluation

Evaluation metrics:

| Metric | Description |
|---|---|
| MAE | Mean Absolute Error |
| MSE | Mean Squared Error |
| RMSE | Root Mean Squared Error |
| R² Score | Prediction accuracy |

---

# 11. HADOOP IMPLEMENTATION

## Starting Hadoop Services

```bash
start-dfs.sh
start-yarn.sh
```

---

## Upload Dataset to HDFS

```bash
hdfs dfs -put data.txt /input/
```

---

## Verify Files

```bash
hdfs dfs -ls /input/
```

---

## Run MapReduce Job

```bash
hadoop jar energyprediction.jar input output
```

---

## View Output

```bash
hdfs dfs -cat /output/part-00000
```

---

# 12. MACHINE LEARNING MODELS

# Linear Regression

Linear Regression predicts energy consumption based on independent variables.

## Advantages

- Simple implementation
- Fast execution
- Easy interpretation

## Limitations

- Poor handling of nonlinear data

---

# Random Forest Regression

Random Forest uses multiple decision trees for prediction.

## Advantages

- Higher prediction accuracy
- Handles nonlinear relationships
- Better robustness

## Limitations

- Higher computational cost

---

# 13. CODE SNIPPETS

## Python Data Loading

```python
import pandas as pd

data = pd.read_csv('household_power_consumption.txt', sep=';')
print(data.head())
```

---

## Data Cleaning

```python
# Replace missing values

data.replace('?', None, inplace=True)
data.dropna(inplace=True)
```

---

## Feature Engineering

```python
# Convert date and time

data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])

data['Hour'] = data['Datetime'].dt.hour
data['Day'] = data['Datetime'].dt.day
data['Month'] = data['Datetime'].dt.month
```

---

## Train-Test Split

```python
from sklearn.model_selection import train_test_split

X = data[['Voltage', 'Global_intensity', 'Hour']]
y = data['Global_active_power']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

---

## Linear Regression Model

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)
```

---

## Random Forest Model

```python
from sklearn.ensemble import RandomForestRegressor

rf = RandomForestRegressor(n_estimators=100)
rf.fit(X_train, y_train)
```

---

## Model Evaluation

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

predictions = rf.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(mae)
print(mse)
print(r2)
```

---

# 14. RESULTS AND ANALYSIS

## Observations

- Random Forest produced more accurate predictions.
- Peak energy consumption periods were successfully identified.
- Hadoop efficiently processed large datasets.
- Distributed processing reduced computation time.

## Sample Output Analysis

| Model | Accuracy |
|---|---|
| Linear Regression | Moderate |
| Random Forest | High |

## Performance Improvements

| Feature | Improvement |
|---|---|
| Distributed Storage | Better scalability |
| Parallel Processing | Faster execution |
| ML Prediction | Higher accuracy |

---

# 15. ADVANTAGES

## Technical Advantages

- Distributed architecture
- Scalable processing
- Fault tolerance
- Efficient data handling
- Parallel computation

## Business Advantages

- Better energy management
- Reduced operational costs
- Smart grid optimization
- Improved forecasting

---

# 16. LIMITATIONS

- MapReduce is slower for iterative tasks
- Hadoop setup complexity is high
- Real-time prediction is difficult
- Requires large computational resources

---

# 17. FUTURE ENHANCEMENTS

## Advanced Big Data Technologies

- Apache Spark integration
- Kafka-based streaming
- Real-time analytics

## Advanced Machine Learning

- Deep Learning models
- LSTM neural networks
- Hybrid forecasting systems

## Cloud Integration

- AWS EMR
- Google Cloud Dataproc
- Azure HDInsight

## Dashboard Development

- Real-time monitoring dashboard
- Power BI integration
- Interactive visualization

---

# 18. CONCLUSION

This project successfully demonstrates the integration of Hadoop and Machine Learning for scalable energy consumption prediction.

The proposed system:

- Efficiently handles large datasets
- Provides scalable distributed processing
- Predicts energy usage accurately
- Supports future smart grid applications

By combining Big Data analytics with predictive modeling, the system becomes highly suitable for modern intelligent energy management systems.

---

# 19. REFERENCES

1. UCI Machine Learning Repository
2. Apache Hadoop Official Documentation
3. Scikit-learn Documentation
4. Python Pandas Documentation
5. Hadoop MapReduce Guide
6. Research Papers on Energy Forecasting

---

# APPENDIX

# Possible Project Folder Structure

```text
energy-consumption-prediction/
│
├── dataset/
│   └── household_power_consumption.txt
│
├── hadoop/
│   ├── mapper.py
│   ├── reducer.py
│   └── run.sh
│
├── ml/
│   ├── train_model.py
│   ├── evaluate.py
│   └── predict.py
│
├── output/
│   └── prediction_results.csv
│
├── notebooks/
│   └── analysis.ipynb
│
├── requirements.txt
│
└── README.md
```

---

# SOFTWARE REQUIREMENTS

| Software | Version |
|---|---|
| Python | 3.x |
| Hadoop | 3.x |
| Java | JDK 8+ |
| Linux | Ubuntu 20+ |
| Scikit-learn | Latest |

---

# HARDWARE REQUIREMENTS

| Hardware | Requirement |
|---|---|
| RAM | Minimum 8 GB |
| Processor | Intel i5 or higher |
| Storage | 100 GB |
| Network | Distributed cluster support |

---

# KEY LEARNING OUTCOMES

After completing this project, students can understand:

- Big Data fundamentals
- Hadoop ecosystem
- Distributed computing
- MapReduce programming
- Machine Learning workflow
- Predictive analytics
- Smart grid technologies
- Scalable data engineering

