"""Filter tool — filters rows in a CSV by column value with various operators."""

import os
import pandas as pd
import numpy as np


UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")


def filter_data(filename: str, column: str, operator: str, value) -> dict:
    """
    Filter rows in a CSV file based on a column condition.

    Args:
        filename: Name of the CSV file.
        column: Column name to filter on.
        operator: One of "eq", "gt", "lt", "gte", "lte", "contains".
        value: The value to compare against.

    Returns:
        Dictionary with filtered row count and a 10-row preview.
    """
    try:
        filepath = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(filepath):
            return {"error": f"File '{filename}' not found."}

        df = pd.read_csv(filepath)

        if column not in df.columns:
            return {"error": f"Column '{column}' not found. Available columns: {list(df.columns)}"}

        supported_operators = ["eq", "gt", "lt", "gte", "lte", "contains"]
        if operator not in supported_operators:
            return {"error": f"Unsupported operator '{operator}'. Use one of: {supported_operators}"}

        col_data = df[column]

        # Try to cast value for numeric comparisons
        if operator in ("gt", "lt", "gte", "lte"):
            try:
                value = float(value)
            except (ValueError, TypeError):
                return {"error": f"Value '{value}' cannot be converted to a number for operator '{operator}'."}

        # Apply filter
        if operator == "eq":
            # Handle numeric equality too
            if pd.api.types.is_numeric_dtype(col_data):
                try:
                    mask = col_data == float(value)
                except (ValueError, TypeError):
                    mask = col_data.astype(str) == str(value)
            else:
                mask = col_data.astype(str) == str(value)
        elif operator == "gt":
            mask = col_data > value
        elif operator == "lt":
            mask = col_data < value
        elif operator == "gte":
            mask = col_data >= value
        elif operator == "lte":
            mask = col_data <= value
        elif operator == "contains":
            mask = col_data.astype(str).str.contains(str(value), case=False, na=False)
        else:
            mask = pd.Series([False] * len(df))

        filtered_df = df[mask]
        preview = filtered_df.head(10).to_dict(orient="records")

        # Clean up NaN values for JSON serialization
        clean_preview = []
        for row in preview:
            clean_row = {}
            for k, v in row.items():
                if isinstance(v, float) and np.isnan(v):
                    clean_row[k] = None
                elif isinstance(v, (np.integer,)):
                    clean_row[k] = int(v)
                elif isinstance(v, (np.floating,)):
                    clean_row[k] = round(float(v), 4)
                else:
                    clean_row[k] = v
            clean_preview.append(clean_row)

        return {
            "column": column,
            "operator": operator,
            "value": str(value),
            "total_rows": len(df),
            "filtered_rows": len(filtered_df),
            "match_percentage": round(len(filtered_df) / len(df) * 100, 2) if len(df) > 0 else 0,
            "preview": clean_preview,
        }

    except Exception as e:
        return {"error": f"Filter operation failed: {str(e)}"}
