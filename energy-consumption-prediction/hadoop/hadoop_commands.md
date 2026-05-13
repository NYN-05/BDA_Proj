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

## View Output in HDFS
```bat
docker exec -i hadoop-namenode hdfs dfs -cat /output_energy/part-00000
```

## Fetch Output to Local File
```bat
cd hadoop
fetch_output.bat
```
