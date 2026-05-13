from pathlib import Path

from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, dayofmonth, hour, month


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / "output" / "mapreduce_hourly_avg.csv"
    output_path = project_root / "output" / "spark_predictions.csv"

    spark = (
        SparkSession.builder.appName("EnergyForecastingLocal")
        .master("local[*]")
        .getOrCreate()
    )

    data = spark.read.csv(
        str(input_path), header=False, schema="date_hour STRING, avg_power DOUBLE"
    )
    data = data.withColumn("hour", hour(col("date_hour")))
    data = data.withColumn("day", dayofmonth(col("date_hour")))
    data = data.withColumn("month", month(col("date_hour")))

    assembler = VectorAssembler(inputCols=["hour", "day", "month"], outputCol="features")
    data = assembler.transform(data)

    train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)
    lr = LinearRegression(featuresCol="features", labelCol="avg_power")
    model = lr.fit(train_data)

    predictions = model.transform(test_data)
    selected = predictions.select("date_hour", "avg_power", "prediction")
    selected.show(20, truncate=False)
    selected.toPandas().to_csv(output_path, index=False)

    spark.stop()


if __name__ == "__main__":
    main()
