"""Top N tool — finds the top N values in a column by count, sum, or mean."""

import os
import pandas as pd
import numpy as np


UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")


def top_n_values(filename: str, column: str, n: int = 10, metric: str = "count") -> dict:
    """
    Find the top N values in a column aggregated by a given metric.

    Args:
        filename: Name of the CSV file.
        column: Column name to analyze.
        n: Number of top results to return.
        metric: Aggregation method — "count", "sum", "mean", "max", or "min".

    Returns:
        Dictionary with sorted results as a list of {value, metric_value} dicts.
    """
    try:
        filepath = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(filepath):
            return {"error": f"File '{filename}' not found."}

        df = pd.read_csv(filepath)

        if column not in df.columns:
            return {"error": f"Column '{column}' not found. Available columns: {list(df.columns)}"}

        if metric == "count":
            result_series = df[column].value_counts().head(n)
            results = [
                {"value": str(val), "metric_value": int(count)}
                for val, count in result_series.items()
            ]
        elif metric in ("sum", "mean", "max", "min"):
            # Find a numeric column to aggregate by if grouping
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                return {"error": f"No numeric columns available for {metric} aggregation."}
            
            # Use the first numeric column that isn't the grouping column
            agg_col = None
            for nc in numeric_cols:
                if nc != column:
                    agg_col = nc
                    break
            if agg_col is None:
                agg_col = numeric_cols[0]

            if metric == "sum":
                grouped = df.groupby(column)[agg_col].sum().nlargest(n)
            elif metric == "mean":
                grouped = df.groupby(column)[agg_col].mean().nlargest(n)
            elif metric == "max":
                grouped = df.groupby(column)[agg_col].max().nlargest(n)
            elif metric == "min":
                grouped = df.groupby(column)[agg_col].min().nsmallest(n)

            results = [
                {"value": str(val), "metric_value": round(float(metric_val), 2) if isinstance(metric_val, float) else metric_val}
                for val, metric_val in grouped.items()
            ]

            return {
                "column": column,
                "metric": metric,
                "aggregated_by": agg_col,
                "n": n,
                "results": results,
            }
        else:
            return {"error": f"Unsupported metric '{metric}'. Use 'count', 'sum', 'mean', 'max', or 'min'."}

        return {
            "column": column,
            "metric": metric,
            "n": n,
            "results": results,
        }

    except Exception as e:
        return {"error": f"Top N analysis failed: {str(e)}"}
