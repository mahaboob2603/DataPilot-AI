"""MCP Server — Tool registry and dispatcher for DataPilot AI."""

import json
from tools.csv_loader import load_csv
from tools.summarizer import summarize_data
from tools.plotter import plot_distribution
from tools.top_n import top_n_values
from tools.filter_tool import filter_data


class MCPServer:
    """
    Model Context Protocol server that manages tool registration,
    schema generation, and tool dispatch for the DataPilot agent.
    """

    def __init__(self):
        # Registry: map tool name → callable
        self.tool_registry: dict = {
            "load_csv": load_csv,
            "summarize_data": summarize_data,
            "plot_distribution": plot_distribution,
            "top_n_values": top_n_values,
            "filter_data": filter_data,
        }

        # Tool schemas in Anthropic tool-use format
        self._tool_schemas: dict = {
            "load_csv": {
                "name": "load_csv",
                "description": (
                    "Load a CSV file and return its schema information including column names, "
                    "data types, row count, a 5-row preview, and missing value counts. "
                    "Always call this first to understand the dataset structure."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The uploaded CSV filename",
                        }
                    },
                    "required": ["filename"],
                },
            },
            "summarize_data": {
                "name": "summarize_data",
                "description": (
                    "Compute comprehensive summary statistics for the dataset: "
                    "descriptive stats for numeric columns (mean, std, min, max, quartiles), "
                    "value counts for categorical columns (top 10), null percentages, "
                    "duplicate row count, and memory usage. Use this for 'summarize', "
                    "'describe', or 'overview' questions."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The uploaded CSV filename",
                        },
                        "columns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of specific columns to summarize. If omitted, all columns are summarized.",
                        },
                    },
                    "required": ["filename"],
                },
            },
            "plot_distribution": {
                "name": "plot_distribution",
                "description": (
                    "Generate a distribution chart for a given column. "
                    "For numeric columns, produces a histogram with KDE curve. "
                    "For categorical columns, produces a horizontal bar chart of top values. "
                    "Use this for 'show distribution', 'plot', 'chart', or 'visualize' questions."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The uploaded CSV filename",
                        },
                        "column": {
                            "type": "string",
                            "description": "Column name to plot",
                        },
                        "chart_type": {
                            "type": "string",
                            "enum": ["auto", "histogram", "bar"],
                            "description": "Chart type. 'auto' will detect based on column data type.",
                            "default": "auto",
                        },
                    },
                    "required": ["filename", "column"],
                },
            },
            "top_n_values": {
                "name": "top_n_values",
                "description": (
                    "Find the top N values in a column by count, sum, mean, max, or min. "
                    "Use this to answer questions like 'what are the top-selling products', "
                    "'which region has highest revenue', 'most common categories', or 'highest speed'."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The uploaded CSV filename",
                        },
                        "column": {
                            "type": "string",
                            "description": "Column name to analyze",
                        },
                        "n": {
                            "type": "integer",
                            "description": "Number of top results to return",
                            "default": 10,
                        },
                        "metric": {
                            "type": "string",
                            "enum": ["count", "sum", "mean", "max", "min"],
                            "description": "Aggregation method",
                        },
                    },
                    "required": ["filename", "column"],
                },
            },
            "filter_data": {
                "name": "filter_data",
                "description": (
                    "Filter rows in the CSV by a column condition. "
                    "Supports operators: eq (equals), gt (greater than), lt (less than), "
                    "gte (>=), lte (<=), contains (substring match). "
                    "Returns the count of matching rows and a 10-row preview."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "The uploaded CSV filename",
                        },
                        "column": {
                            "type": "string",
                            "description": "Column name to filter on",
                        },
                        "operator": {
                            "type": "string",
                            "enum": ["eq", "gt", "lt", "gte", "lte", "contains"],
                            "description": "Comparison operator",
                        },
                        "value": {
                            "type": "string",
                            "description": "The value to compare against",
                        },
                    },
                    "required": ["filename", "column", "operator", "value"],
                },
            },
        }

    def get_tool_definitions(self) -> list[dict]:
        """Return all tool schemas for the Claude API call."""
        return list(self._tool_schemas.values())

    def get_tool_schema(self, tool_name: str) -> dict | None:
        """Return the schema for a specific tool."""
        return self._tool_schemas.get(tool_name)

    def call_tool(self, tool_name: str, parameters: dict) -> dict:
        """
        Validate and call a registered tool with the given parameters.

        Args:
            tool_name: Name of the tool to call.
            parameters: Dictionary of parameters to pass to the tool.

        Returns:
            Result dictionary from the tool, or an error dict.
        """
        if tool_name not in self.tool_registry:
            return {"error": f"Unknown tool '{tool_name}'. Available tools: {list(self.tool_registry.keys())}"}

        tool_fn = self.tool_registry[tool_name]

        # Validate required parameters
        schema = self._tool_schemas.get(tool_name, {})
        required = schema.get("input_schema", {}).get("required", [])
        for req_param in required:
            if req_param not in parameters:
                return {"error": f"Missing required parameter '{req_param}' for tool '{tool_name}'."}

        try:
            print(f"  [TOOL] Calling tool: {tool_name}({json.dumps(parameters, default=str)[:200]})")
            result = tool_fn(**parameters)
            print(f"  [OK] Tool '{tool_name}' returned successfully")
            return result
        except TypeError as e:
            return {"error": f"Invalid parameters for tool '{tool_name}': {str(e)}"}
        except Exception as e:
            return {"error": f"Tool '{tool_name}' failed: {str(e)}"}
