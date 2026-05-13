
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
