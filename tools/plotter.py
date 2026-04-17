"""Plotter tool — generates distribution charts for CSV columns."""

import os
import time
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns


UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
CHART_OUTPUT_DIR = os.getenv("CHART_OUTPUT_DIR", "./outputs")


def plot_distribution(filename: str, column: str, chart_type: str = "auto") -> dict:
    """
    Generate a distribution chart for a column in a CSV file.

    Args:
        filename: Name of the CSV file in the uploads directory.
        column: Column name to plot.
        chart_type: "auto" (detect), "histogram", or "bar".

    Returns:
        Dictionary with chart_path, chart_url, column name, and chart_type used.
    """
    try:
        filepath = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(filepath):
            return {"error": f"File '{filename}' not found."}

        df = pd.read_csv(filepath)

        if column not in df.columns:
            return {"error": f"Column '{column}' not found. Available columns: {list(df.columns)}"}

        # Ensure output directory exists
        os.makedirs(CHART_OUTPUT_DIR, exist_ok=True)

        # Set Seaborn style
        sns.set_theme(style="whitegrid", palette="viridis")
        fig, ax = plt.subplots(figsize=(10, 6))

        # Determine chart type
        col_data = df[column].dropna()
        is_numeric = pd.api.types.is_numeric_dtype(col_data)

        if chart_type == "auto":
            chart_type = "histogram" if is_numeric else "bar"

        if chart_type == "histogram" and is_numeric:
            sns.histplot(col_data, bins=30, kde=True, ax=ax, color="#6366f1", edgecolor="#4f46e5")
            ax.set_title(f"Distribution of {column}", fontsize=16, fontweight="bold", pad=15)
            ax.set_xlabel(column, fontsize=12)
            ax.set_ylabel("Frequency", fontsize=12)
        elif chart_type == "bar" or not is_numeric:
            chart_type = "bar"
            value_counts = col_data.value_counts().head(20)
            colors = sns.color_palette("viridis", len(value_counts))
            value_counts.plot(kind="barh", ax=ax, color=colors, edgecolor="white")
            ax.set_title(f"Top Values in {column}", fontsize=16, fontweight="bold", pad=15)
            ax.set_xlabel("Count", fontsize=12)
            ax.set_ylabel(column, fontsize=12)
        else:
            return {"error": f"Unsupported chart_type '{chart_type}'. Use 'auto', 'histogram', or 'bar'."}

        ax.tick_params(labelsize=10)
        plt.tight_layout()

        # Save chart
        timestamp = int(time.time())
        base_name = os.path.splitext(filename)[0]
        chart_filename = f"{base_name}_{column}_{timestamp}.png"
        chart_path = os.path.join(CHART_OUTPUT_DIR, chart_filename)
        fig.savefig(chart_path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)

        chart_url = f"/chart/{chart_filename}"

        return {
            "chart_path": chart_path,
            "chart_url": chart_url,
            "column": column,
            "chart_type": chart_type,
        }

    except Exception as e:
        return {"error": f"Plot generation failed: {str(e)}"}
