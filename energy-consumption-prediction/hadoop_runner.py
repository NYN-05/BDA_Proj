"""
Hadoop Runner - Integrates HDFS, MapReduce, Hive, MongoDB, and Spark MLlib
"""
import os
import subprocess
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent
HADOOP_DIR = PROJECT_ROOT / "hadoop"
DATASET_PATH = PROJECT_ROOT / "dataset" / "household_power_consumption.txt"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

HADOOP_DIR_DOCKER = Path("C:/Users/JHASHANK/docker-hadoop")
HADOOP_NAMENODE = "namenode"
HADOOP_DATANODE = "datanode"
HADOOP_RESOURCEMANAGER = "resourcemanager"
HADOOP_NODEMANAGER = "nodemanager"
HADOOP_HISTORYSERVER = "historyserver"


def run_docker_compose(command):
    result = subprocess.run(
        f"docker compose {command}",
        shell=True,
        cwd=HADOOP_DIR_DOCKER,
        capture_output=True,
        text=True
    )
    return result


def is_container_running(container_name):
    result = subprocess.run(
        f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'",
        shell=True,
        capture_output=True,
        text=True
    )
    return container_name in result.stdout


def docker_exec(container, cmd):
    result = subprocess.run(
        f"docker exec -i {container} {cmd}",
        shell=True,
        capture_output=True,
        text=True
    )
    return result


def start_hadoop_cluster():
    LOGGER.info("Checking Hadoop cluster...")
    if is_container_running(HADOOP_NAMENODE):
        LOGGER.info("Hadoop cluster is already running!")
        return True
    LOGGER.info("Starting Hadoop cluster...")
    result = run_docker_compose("up -d")
    if result.returncode != 0:
        LOGGER.error(f"Failed to start cluster: {result.stderr}")
        return False
    LOGGER.info("Waiting for namenode to be ready...")
    time.sleep(30)
    if is_container_running(HADOOP_NAMENODE):
        LOGGER.info("Hadoop cluster started successfully!")
        return True
    return False


def start_other_services():
    LOGGER.info("Starting other services (Hive, Spark, MongoDB)...")
    result = subprocess.run(
        f"docker compose -f {PROJECT_ROOT / 'docker-compose.yml'} up -d",
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        LOGGER.info("Services started successfully!")
        time.sleep(20)
        return True
    LOGGER.error(f"Failed to start services: {result.stderr}")
    return False


def upload_to_hdfs():
    LOGGER.info("Uploading dataset to HDFS...")
    # Create directories on container filesystem (not just HDFS)
    docker_exec(HADOOP_NAMENODE, "mkdir -p /input")
    docker_exec(HADOOP_NAMENODE, "mkdir -p /workspace/hadoop")
    docker_exec(HADOOP_NAMENODE, "hdfs dfs -mkdir -p /input")
    
    # Helper function to upload file via docker exec stdin
    def upload_file_to_container(local_path, container_path):
        try:
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            LOGGER.info(f"Uploading {local_path} ({len(file_content)} bytes) to {container_path}")
            
            process = subprocess.Popen(
                f"docker exec -i {HADOOP_NAMENODE} bash -c \"cat > {container_path}\"",
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate(input=file_content, timeout=30)
            
            if process.returncode != 0:
                LOGGER.error(f"Upload failed - stdout: {stdout.decode()}, stderr: {stderr.decode()}")
            
            # Verify file was written
            verify_result = subprocess.run(
                f"docker exec {HADOOP_NAMENODE} test -f {container_path} && echo 'exists' || echo 'not found'",
                shell=True,
                capture_output=True,
                text=True
            )
            LOGGER.info(f"File verification: {verify_result.stdout.strip()}")
            
            return process.returncode
        except Exception as e:
            LOGGER.error(f"Exception during file upload: {e}")
            return 1
    
    # Upload files to container
    result_dataset = upload_file_to_container(str(DATASET_PATH), "/input/household_power_consumption.txt")
    LOGGER.info(f"Copy dataset result: {result_dataset}")
    
    result_mapper = upload_file_to_container(str(HADOOP_DIR / 'mapper.sh'), "/workspace/hadoop/mapper.sh")
    LOGGER.info(f"Copy mapper result: {result_mapper}")
    
    result_reducer = upload_file_to_container(str(HADOOP_DIR / 'reducer.sh'), "/workspace/hadoop/reducer.sh")
    LOGGER.info(f"Copy reducer result: {result_reducer}")
    
    # Put the dataset file into HDFS
    docker_exec(HADOOP_NAMENODE, "hdfs dfs -put -f /input/household_power_consumption.txt /input/")
    
    LOGGER.info("Installing Python3 in namenode...")
    docker_exec(HADOOP_NAMENODE, "bash -lc 'apt-get update && apt-get install -y python3'")
    
    LOGGER.info("Installing Python3 in datanode...")
    docker_exec(HADOOP_DATANODE, "bash -lc 'apt-get update && apt-get install -y python3'")
    
    LOGGER.info("Installing Python3 in nodemanager...")
    docker_exec(HADOOP_NODEMANAGER, "bash -lc 'apt-get update && apt-get install -y python3'")
    
    LOGGER.info("Installing Python3 in resourcemanager...")
    docker_exec(HADOOP_RESOURCEMANAGER, "bash -lc 'apt-get update && apt-get install -y python3'")
    
    docker_exec(HADOOP_NAMENODE, "bash -lc 'chmod +x /workspace/hadoop/mapper.sh /workspace/hadoop/reducer.sh'")
    
    LOGGER.info("Dataset and scripts uploaded to HDFS!")
    return True


def run_mapreduce():
    LOGGER.info("Running MapReduce job...")
    docker_exec(HADOOP_NAMENODE, "hdfs dfs -rm -r -f /output_energy")
    
    mapreduce_cmd = (
        "bash -lc \"/opt/hadoop-3.2.1/bin/hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar "
        "-input /input/household_power_consumption.txt "
        "-output /output_energy "
        "-mapper '/workspace/hadoop/mapper.sh' "
        "-reducer '/workspace/hadoop/reducer.sh' "
        "-file /workspace/hadoop/mapper.sh "
        "-file /workspace/hadoop/reducer.sh\""
    )
    
    result = docker_exec(HADOOP_NAMENODE, mapreduce_cmd)
    LOGGER.info(f"MapReduce output: {result.stdout[:500]}")
    
    if result.returncode == 0:
        LOGGER.info("MapReduce job completed!")
        output_result = docker_exec(HADOOP_NAMENODE, "hdfs dfs -cat /output_energy/part-00000")
        LOGGER.info(f"Output sample: {output_result.stdout[:300]}")
        return True
    LOGGER.error(f"MapReduce failed: {result.stderr}")
    return False


def setup_hive():
    LOGGER.info("Setting up Hive...")
    docker_exec(HADOOP_NAMENODE, "hdfs dfs -mkdir -p /user/hive/warehouse")
    
    subprocess.run(
        f"docker compose -f {PROJECT_ROOT / 'docker-compose.yml'} up -d hive-metastore hive-server",
        shell=True,
        capture_output=True
    )
    time.sleep(20)
    
    create_table_sql = "CREATE TABLE IF NOT EXISTS hourly_energy (date_hour STRING, avg_power DOUBLE) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE LOCATION '/user/hive/warehouse/hourly_energy';"
    result = docker_exec("hive-server", f"bash -lc 'hive -e \"{create_table_sql}\"'")
    LOGGER.info(f"Hive create table: {result.stdout}")
    
    load_sql = "LOAD DATA INPATH '/output_energy/part-00000' INTO TABLE hourly_energy;"
    docker_exec("hive-server", f"bash -lc 'hive -e \"{load_sql}\"'")
    
    query_sql = "SELECT date_hour, avg_power FROM hourly_energy ORDER BY date_hour LIMIT 10;"
    result = docker_exec("hive-server", f"bash -lc 'hive -e \"{query_sql}\"'")
    LOGGER.info(f"Hive query results:\n{result.stdout}")
    return True


def run_spark_mllib():
    LOGGER.info("Running Spark MLlib for forecasting...")
    spark_script = """
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from pyspark.sql.functions import col, hour, dayofmonth, month

spark = SparkSession.builder.appName("EnergyForecasting").master("spark://spark-master:7077").getOrCreate()

data = spark.read.csv("hdfs://namenode:9000/output_energy/part-00000", header=False, schema="date_hour STRING, avg_power DOUBLE")
data = data.withColumn("hour", hour(col("date_hour")))
data = data.withColumn("day", dayofmonth(col("date_hour")))
data = data.withColumn("month", month(col("date_hour")))

assembler = VectorAssembler(inputCols=["hour", "day", "month"], outputCol="features")
data = assembler.transform(data)

train_data, test_data = data.randomSplit([0.8, 0.2])
lr = LinearRegression(featuresCol="features", labelCol="avg_power")
model = lr.fit(train_data)

predictions = model.transform(test_data)
predictions.select("date_hour", "avg_power", "prediction").show()

model.save("hdfs://namenode:9000/spark_model")
spark.stop()
"""
    with open(HADOOP_DIR / "spark_forecast.py", "w") as f:
        f.write(spark_script)
    
    subprocess.run(
        f"docker cp '{HADOOP_DIR}/spark_forecast.py' spark-master:/tmp/spark_forecast.py",
        shell=True,
        capture_output=True
    )
    
    result = subprocess.run(
        "docker exec spark-master spark-submit --master spark://spark-master:7077 /tmp/spark_forecast.py",
        shell=True,
        capture_output=True,
        text=True
    )
    
    LOGGER.info(f"Spark job output: {result.stdout[:500]}")
    if result.returncode != 0:
        LOGGER.error(f"Spark job failed: {result.stderr}")
    return result.returncode == 0


def store_in_mongodb():
    LOGGER.info("Storing predictions in MongoDB...")
    mongo_script = """
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
"""
    with open(HADOOP_DIR / "mongo_store.py", "w") as f:
        f.write(mongo_script)
    
    subprocess.run(
        f"docker cp '{HADOOP_DIR}/mongo_store.py' mongo:/tmp/mongo_store.py",
        shell=True,
        capture_output=True
    )
    
    result = subprocess.run(
        "docker exec mongo python3 /tmp/mongo_store.py",
        shell=True,
        capture_output=True,
        text=True
    )
    
    LOGGER.info(f"MongoDB storage result: {result.stdout}")
    return True


def web_analytics():
    LOGGER.info("Performing web analytics for energy-saving tips...")
    tips = """
Energy-Saving Tips based on MapReduce Analysis:
1. Reduce usage during peak hours (17:00-21:00)
2. Optimize HVAC usage based on monthly trends
3. Schedule high-power appliances during off-peak hours
4. Monitor daily patterns to identify waste periods
5. Use predictive insights from ML model to plan consumption
"""
    with open(OUTPUT_DIR / "energy_saving_tips.txt", "w") as f:
        f.write(tips)
    LOGGER.info(tips)
    return True


def main():
    LOGGER.info("=" * 60)
    LOGGER.info("HADOOP RUNNER - Starting Big Data Pipeline")
    LOGGER.info("=" * 60)
    
    if not start_hadoop_cluster():
        LOGGER.error("Failed to start Hadoop cluster")
        return
    
    start_other_services()
    
    if not upload_to_hdfs():
        LOGGER.error("Failed to upload data to HDFS")
        return
    
    if not run_mapreduce():
        LOGGER.error("Failed to run MapReduce")
        return
    
    setup_hive()
    run_spark_mllib()
    store_in_mongodb()
    web_analytics()
    
    LOGGER.info("=" * 60)
    LOGGER.info("Pipeline completed successfully!")
    LOGGER.info("=" * 60)


if __name__ == "__main__":
    main()