CREATE TABLE IF NOT EXISTS hourly_energy (
  date_hour STRING,
  avg_power DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/hourly_energy';

LOAD DATA INPATH '/output_energy/part-00000' OVERWRITE INTO TABLE hourly_energy;

SELECT substr(date_hour, 1, 10) AS day,
       avg(avg_power) AS avg_power
FROM hourly_energy
GROUP BY substr(date_hour, 1, 10)
ORDER BY day
LIMIT 10;