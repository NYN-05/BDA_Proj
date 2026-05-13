@echo off
setlocal
call "%~dp0docker_env.bat"

for /f %%i in ('docker ps --format "{{.Names}}" ^| findstr /i /x "%HADOOP_NAMENODE_CONTAINER%"') do set "FOUND=1"
if not defined FOUND (
  echo Container %HADOOP_NAMENODE_CONTAINER% is not running.
  exit /b 1
)

docker exec -i %HADOOP_NAMENODE_CONTAINER% hdfs dfs -mkdir -p /input
docker exec -i %HADOOP_NAMENODE_CONTAINER% hdfs dfs -put -f /workspace/dataset/household_power_consumption.txt /input/

docker exec -i %HADOOP_NAMENODE_CONTAINER% hdfs dfs -ls /input

endlocal
