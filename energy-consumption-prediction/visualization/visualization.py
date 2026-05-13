import logging
from pathlib import Path
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

LOGGER = logging.getLogger(__name__)


def plot_monthly_usage(processed_path: Path, charts_dir: Path):
    df = pd.read_csv(processed_path, parse_dates=["MonthStart", "TargetMonthStart"])
    df = df.sort_values("TargetMonthStart")

    plt.figure(figsize=(12, 5))
    plt.plot(df["TargetMonthStart"], df["Next_month_kwh"], linewidth=1)
    plt.title("Monthly Energy Usage (kWh)")
    plt.xlabel("Month")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    plt.savefig(charts_dir / "monthly_usage.png")
    plt.close()


def plot_feature_importance(model_path: Path, processed_path: Path, charts_dir: Path):
    model = joblib.load(model_path)
    df = pd.read_csv(processed_path, parse_dates=["MonthStart", "TargetMonthStart"])
    feature_cols = df.drop(columns=["MonthStart", "TargetMonthStart", "Next_month_kwh"]).columns

    if not hasattr(model, "feature_importances_"):
        LOGGER.warning("Model does not expose feature importances")
        return

    importances = pd.Series(model.feature_importances_, index=feature_cols)
    importances = importances.sort_values(ascending=False)

    plt.figure(figsize=(10, 5))
    sns.barplot(x=importances.values, y=importances.index)
    plt.title("Feature Importance (Random Forest)")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(charts_dir / "feature_importance.png")
    plt.close()


def plot_correlation_heatmap(processed_path: Path, charts_dir: Path):
    df = pd.read_csv(processed_path, parse_dates=["MonthStart", "TargetMonthStart"])
    df = df.drop(columns=["MonthStart", "TargetMonthStart"])

    plt.figure(figsize=(10, 6))
    sns.heatmap(df.corr(numeric_only=True), cmap="coolwarm", center=0)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(charts_dir / "correlation_heatmap.png")
    plt.close()


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    root = Path(__file__).resolve().parents[1]
    charts_dir = root / "visualization" / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    processed_path = root / "output" / "processed_monthly.csv"
    model_path = root / "ml" / "saved_models" / "random_forest.joblib"

    plot_monthly_usage(processed_path, charts_dir)
    plot_feature_importance(model_path, processed_path, charts_dir)
    plot_correlation_heatmap(processed_path, charts_dir)

    LOGGER.info("Saved charts to %s", charts_dir)


if __name__ == "__main__":
    main()
