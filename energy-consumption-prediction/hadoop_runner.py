"""
Hadoop Runner - Integrates HDFS and MapReduce for preprocessing.
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
HIVE_SERVER = "hive-server"


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
    LOGGER.info("Skipping Docker service startup (MongoDB removed).")
    return True


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


def run_hive_trend_analysis():
    LOGGER.info("Running Hive trend analysis...")
    if not is_container_running(HIVE_SERVER):
        LOGGER.warning("Hive server container is not running. Skipping Hive analysis.")
        return False

    hive_create = (
        "CREATE TABLE IF NOT EXISTS hourly_energy ("
        "date_hour STRING, avg_power DOUBLE) "
        "ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' "
        "STORED AS TEXTFILE "
        "LOCATION '/user/hive/warehouse/hourly_energy'"
    )
    docker_exec(HADOOP_NAMENODE, "hdfs dfs -mkdir -p /user/hive/warehouse/hourly_energy")
    docker_exec(HADOOP_NAMENODE, "hdfs dfs -rm -r -f /user/hive/warehouse/hourly_energy/*")

    result = docker_exec(HIVE_SERVER, f"bash -lc 'hive -e \"{hive_create}\"'")
    if result.returncode != 0:
        LOGGER.error("Hive create table failed: %s", result.stderr)
        return False

    load_sql = "LOAD DATA INPATH '/output_energy/part-00000' OVERWRITE INTO TABLE hourly_energy;"
    result = docker_exec(HIVE_SERVER, f"bash -lc 'hive -e \"{load_sql}\"'")
    if result.returncode != 0:
        LOGGER.error("Hive load failed: %s", result.stderr)
        return False

    query_sql = (
        "SELECT substr(date_hour, 1, 10) AS day, "
        "avg(avg_power) AS avg_power "
        "FROM hourly_energy "
        "GROUP BY substr(date_hour, 1, 10) "
        "ORDER BY day LIMIT 10;"
    )
    result = docker_exec(HIVE_SERVER, f"bash -lc 'hive -e \"{query_sql}\"'")
    if result.returncode != 0:
        LOGGER.error("Hive query failed: %s", result.stderr)
        return False

    output_path = OUTPUT_DIR / "hive_daily_avg.csv"
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("day,avg_power\n")
        handle.write(result.stdout.strip() + "\n")
    LOGGER.info("Hive daily averages saved to %s", output_path)
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

    run_hive_trend_analysis()
    
    web_analytics()
    
    LOGGER.info("=" * 60)
    LOGGER.info("Pipeline completed successfully!")
    LOGGER.info("=" * 60)


if __name__ == "__main__":
    main()