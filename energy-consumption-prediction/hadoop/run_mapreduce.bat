@echo off
setlocal
call "%~dp0docker_env.bat"

for /f %%i in ('docker ps --format "{{.Names}}" ^| findstr /i /x "%HADOOP_NAMENODE_CONTAINER%"') do set "FOUND=1"
if not defined FOUND (
  echo Container %HADOOP_NAMENODE_CONTAINER% is not running.
  exit /b 1
)

docker exec -i %HADOOP_NAMENODE_CONTAINER% hdfs dfs -rm -r -f /output_energy

docker exec -i %HADOOP_NAMENODE_CONTAINER% bash -lc "hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-*.jar -input /input/household_power_consumption.txt -output /output_energy -mapper 'python3 /workspace/hadoop/mapper.py' -reducer 'python3 /workspace/hadoop/reducer.py' -file /workspace/hadoop/mapper.py -file /workspace/hadoop/reducer.py"

docker exec -i %HADOOP_NAMENODE_CONTAINER% hdfs dfs -cat /output_energy/part-00000 > ..\output\mapreduce_hourly_avg.csv

endlocal
