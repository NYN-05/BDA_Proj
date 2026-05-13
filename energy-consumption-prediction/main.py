import logging
from pathlib import Path

from preprocessing.preprocess_pipeline import run_preprocessing
from ml.train_random_forest import train_random_forest
from ml.evaluate_model import evaluate
from ml.predict import generate_predictions
from visualization.visualization import (
    plot_monthly_usage,
    plot_feature_importance,
    plot_correlation_heatmap,
)

LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = Path(__file__).resolve().parent

    dataset_path = root / "dataset" / "household_power_consumption.txt"
    processed_path = root / "output" / "processed_monthly.csv"
    scaler_path = root / "ml" / "saved_models" / "scaler.joblib"
    model_path = root / "ml" / "saved_models" / "random_forest.joblib"
    metrics_path = root / "output" / "metrics.txt"
    predictions_path = root / "output" / "next_month_prediction.csv"
    charts_dir = root / "visualization" / "charts"

    run_preprocessing(dataset_path, processed_path, scaler_path)
    train_random_forest(processed_path, model_path)
    evaluate(model_path, processed_path, metrics_path)
    generate_predictions(model_path, scaler_path, dataset_path, predictions_path)

    charts_dir.mkdir(parents=True, exist_ok=True)
    plot_monthly_usage(processed_path, charts_dir)
    plot_feature_importance(model_path, processed_path, charts_dir)
    plot_correlation_heatmap(processed_path, charts_dir)

    LOGGER.info("Pipeline completed successfully")


if __name__ == "__main__":
    main()
