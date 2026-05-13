@echo off
setlocal
call "%~dp0docker_env.bat"

for /f %%i in ('docker ps --format "{{.Names}}" ^| findstr /i /x "%HADOOP_NAMENODE_CONTAINER%"') do set "FOUND=1"
if not defined FOUND (
  echo Container %HADOOP_NAMENODE_CONTAINER% is not running.
  exit /b 1
)

docker exec -i %HADOOP_NAMENODE_CONTAINER% bash -lc "python3 --version" >nul 2>&1
if %errorlevel%==0 (
  echo Python already installed in %HADOOP_NAMENODE_CONTAINER%.
  exit /b 0
)

docker exec -i %HADOOP_NAMENODE_CONTAINER% bash -lc "apt-get update && apt-get install -y python3"

endlocal
