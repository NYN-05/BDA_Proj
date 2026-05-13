# Hadoop Commands (Docker on Windows)

## Start Hadoop Containers
```bat
docker compose up -d
```

## Upload Dataset to HDFS
```bat
cd hadoop
upload_to_hdfs.bat
```

## Run MapReduce (Streaming)
```bat
cd hadoop
run_mapreduce.bat
```

## Run Hive Trend Analysis (Docker Hadoop)
```bat
docker cp hive_trend_analysis.hql hive-server:/tmp/hive_trend_analysis.hql
docker exec -i hive-server hive -f /tmp/hive_trend_analysis.hql
```

## View Output in HDFS
```bat
docker exec -i hadoop-namenode hdfs dfs -cat /output_energy/part-00000
```

## Fetch Output to Local File
```bat
cd hadoop
fetch_output.bat
```
