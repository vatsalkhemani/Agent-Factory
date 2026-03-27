import numpy as np
import pandas as pd

from config import MAX_ROWS, OUTLIER_Z_THRESHOLD, OUTLIER_IQR_MULTIPLIER, SAMPLE_SIZE_FOR_PROFILE
from models import ColumnProfile, DataProfile


class AnalysisToolkit:
    """Predefined analysis operations. The LLM selects tools and parameters;
    this class executes them safely with no arbitrary code."""

    VALID_TOOLS = [
        "describe", "correlation", "distribution", "group_comparison",
        "time_trend", "outlier_detection", "cross_tabulation", "top_n",
        "value_counts", "percentile_analysis",
    ]

    def __init__(self, df: pd.DataFrame):
        self.sampled = False
        if len(df) > MAX_ROWS:
            self.df = df.sample(MAX_ROWS, random_state=42)
            self.sampled = True
        else:
            self.df = df

        self._numeric_cols = list(self.df.select_dtypes(include=[np.number]).columns)
        self._categorical_cols = list(self.df.select_dtypes(include=["object", "category"]).columns)
        self._datetime_cols = list(self.df.select_dtypes(include=["datetime64"]).columns)

    def profile(self) -> DataProfile:
        """Generate a complete data profile (deterministic, no LLM needed)."""
        columns = []
        quality_notes = []

        for col in self.df.columns:
            series = self.df[col]
            non_null = int(series.notna().sum())
            null_count = int(series.isna().sum())
            unique = int(series.nunique())

            # Determine type
            if col in self._numeric_cols:
                dtype = "numeric"
            elif col in self._datetime_cols:
                dtype = "datetime"
            elif unique < min(20, len(self.df) * 0.05) and col in self._categorical_cols:
                dtype = "categorical"
            else:
                dtype = "text" if col in self._categorical_cols else "numeric"

            # Sample values
            sample_vals = [str(v) for v in series.dropna().head(SAMPLE_SIZE_FOR_PROFILE).tolist()]

            profile = ColumnProfile(
                name=col,
                dtype=dtype,
                non_null_count=non_null,
                null_count=null_count,
                unique_count=unique,
                sample_values=sample_vals,
            )

            if dtype == "numeric":
                desc = series.describe()
                profile.mean = round(float(desc.get("mean", 0)), 4)
                profile.median = round(float(series.median()), 4)
                profile.std = round(float(desc.get("std", 0)), 4)
                profile.min_val = round(float(desc.get("min", 0)), 4)
                profile.max_val = round(float(desc.get("max", 0)), 4)

            elif dtype == "categorical":
                vc = series.value_counts().head(8)
                profile.top_values = [str(v) for v in vc.index.tolist()]
                profile.top_counts = vc.values.tolist()

            # Quality notes
            null_pct = null_count / len(self.df) * 100
            if null_pct > 10:
                quality_notes.append(f"Column '{col}' has {null_pct:.0f}% missing values")

            if dtype == "numeric" and profile.std and profile.mean:
                cv = abs(profile.std / profile.mean) if profile.mean != 0 else 0
                if cv > 2:
                    quality_notes.append(f"Column '{col}' has very high variance (CV={cv:.1f})")

        return DataProfile(
            row_count=len(self.df),
            column_count=len(self.df.columns),
            columns=columns,
            data_quality_notes=quality_notes,
            sampled=self.sampled,
        )

    def validate_request(self, tool: str, params: dict) -> tuple[bool, str]:
        """Validate tool name and column parameters exist."""
        if tool not in self.VALID_TOOLS:
            return False, f"Unknown tool '{tool}'"

        for key in ["column", "x_column", "y_column", "group_column", "date_column", "value_column"]:
            if key in params:
                col = params[key]
                if col not in self.df.columns:
                    return False, f"Column '{col}' not found"

        if "columns" in params:
            for col in params["columns"]:
                if col not in self.df.columns:
                    return False, f"Column '{col}' not found"

        return True, ""

    def execute(self, tool: str, params: dict) -> dict:
        """Execute an analysis tool and return results as a dict."""
        method = getattr(self, tool, None)
        if not method:
            return {"error": f"Unknown tool: {tool}", "success": False}
        try:
            result = method(**params)
            return {"data": result, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}

    # --- Analysis Tools ---

    def describe(self, column: str) -> dict:
        """Full descriptive statistics for a column."""
        series = self.df[column].dropna()
        if series.dtype in [np.float64, np.int64, float, int]:
            desc = series.describe()
            return {k: round(float(v), 4) for k, v in desc.items()}
        else:
            return {
                "count": int(series.count()),
                "unique": int(series.nunique()),
                "top": str(series.mode().iloc[0]) if len(series.mode()) > 0 else "",
                "freq": int(series.value_counts().iloc[0]) if len(series) > 0 else 0,
            }

    def correlation(self, columns: list[str] = None) -> dict:
        """Pearson correlation matrix for numeric columns."""
        if columns:
            cols = [c for c in columns if c in self._numeric_cols]
        else:
            cols = self._numeric_cols[:10]  # cap at 10 columns

        if len(cols) < 2:
            return {"error": "Need at least 2 numeric columns for correlation"}

        corr = self.df[cols].corr()
        # Return as nested dict with rounded values
        result = {}
        for c1 in corr.columns:
            result[c1] = {}
            for c2 in corr.columns:
                result[c1][c2] = round(float(corr.loc[c1, c2]), 4)

        # Find top correlations (excluding self-correlation)
        pairs = []
        for i, c1 in enumerate(cols):
            for j, c2 in enumerate(cols):
                if i < j:
                    val = corr.loc[c1, c2]
                    pairs.append({"col1": c1, "col2": c2, "correlation": round(float(val), 4)})
        pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {"matrix": result, "top_pairs": pairs[:5]}

    def distribution(self, column: str, bins: int = 20) -> dict:
        """Histogram data for a column."""
        series = self.df[column].dropna()
        if series.dtype in [np.float64, np.int64, float, int]:
            hist, edges = np.histogram(series, bins=bins)
            return {
                "bin_edges": [round(float(e), 4) for e in edges],
                "counts": [int(c) for c in hist],
                "mean": round(float(series.mean()), 4),
                "median": round(float(series.median()), 4),
                "skew": round(float(series.skew()), 4),
            }
        else:
            vc = series.value_counts().head(bins)
            return {
                "values": [str(v) for v in vc.index.tolist()],
                "counts": [int(c) for c in vc.values.tolist()],
            }

    def group_comparison(self, group_column: str, value_column: str, agg: str = "mean") -> dict:
        """Group by categorical column, aggregate numeric column."""
        valid_aggs = ["mean", "median", "sum", "count", "std", "min", "max"]
        if agg not in valid_aggs:
            agg = "mean"

        grouped = self.df.groupby(group_column)[value_column].agg(agg).reset_index()
        grouped = grouped.sort_values(value_column, ascending=False).head(20)

        return {
            "groups": [str(v) for v in grouped[group_column].tolist()],
            "values": [round(float(v), 4) if pd.notna(v) else 0 for v in grouped[value_column].tolist()],
            "aggregation": agg,
        }

    def time_trend(self, date_column: str, value_column: str, freq: str = "M") -> dict:
        """Resample time series data."""
        df_copy = self.df.copy()
        df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors="coerce")
        df_copy = df_copy.dropna(subset=[date_column])

        if len(df_copy) == 0:
            return {"error": "No valid dates found"}

        df_copy = df_copy.set_index(date_column)
        resampled = df_copy[value_column].resample(freq).mean().dropna()

        return {
            "dates": [str(d.date()) for d in resampled.index],
            "values": [round(float(v), 4) for v in resampled.values],
            "trend_direction": "increasing" if len(resampled) > 1 and resampled.iloc[-1] > resampled.iloc[0] else "decreasing",
            "pct_change": round(float((resampled.iloc[-1] - resampled.iloc[0]) / resampled.iloc[0] * 100), 2) if len(resampled) > 1 and resampled.iloc[0] != 0 else 0,
        }

    def outlier_detection(self, column: str, method: str = "iqr") -> dict:
        """Detect outliers using IQR or z-score."""
        series = self.df[column].dropna()
        if series.dtype not in [np.float64, np.int64, float, int]:
            return {"error": f"Column '{column}' is not numeric"}

        if method == "zscore":
            mean = series.mean()
            std = series.std()
            if std == 0:
                return {"outlier_count": 0, "outlier_pct": 0, "method": "zscore"}
            z_scores = ((series - mean) / std).abs()
            outliers = series[z_scores > OUTLIER_Z_THRESHOLD]
        else:  # IQR
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - OUTLIER_IQR_MULTIPLIER * iqr
            upper = q3 + OUTLIER_IQR_MULTIPLIER * iqr
            outliers = series[(series < lower) | (series > upper)]

        return {
            "outlier_count": int(len(outliers)),
            "outlier_pct": round(len(outliers) / len(series) * 100, 2),
            "total_count": int(len(series)),
            "outlier_examples": [round(float(v), 4) for v in outliers.head(5).tolist()],
            "method": method,
        }

    def cross_tabulation(self, column_1: str, column_2: str) -> dict:
        """Cross-tabulation of two categorical columns."""
        ct = pd.crosstab(self.df[column_1], self.df[column_2])
        # Cap to prevent huge tables
        ct = ct.iloc[:15, :15]

        return {
            "rows": [str(v) for v in ct.index.tolist()],
            "columns": [str(v) for v in ct.columns.tolist()],
            "values": ct.values.tolist(),
        }

    def top_n(self, column: str, n: int = 10, ascending: bool = False) -> dict:
        """Top or bottom N values in a column."""
        n = min(n, 20)
        sorted_df = self.df.nlargest(n, column) if not ascending else self.df.nsmallest(n, column)

        result_cols = [column]
        # Include a few other columns for context
        for c in self.df.columns:
            if c != column and len(result_cols) < 4:
                result_cols.append(c)

        records = sorted_df[result_cols].head(n).to_dict(orient="records")
        # Stringify values
        clean_records = []
        for r in records:
            clean_records.append({k: str(v) for k, v in r.items()})

        return {"records": clean_records, "direction": "bottom" if ascending else "top"}

    def value_counts(self, column: str, top_n: int = 15) -> dict:
        """Value frequency counts."""
        vc = self.df[column].value_counts().head(top_n)
        return {
            "values": [str(v) for v in vc.index.tolist()],
            "counts": [int(c) for c in vc.values.tolist()],
            "total_unique": int(self.df[column].nunique()),
        }

    def percentile_analysis(self, column: str) -> dict:
        """Percentile breakdown of a numeric column."""
        series = self.df[column].dropna()
        if series.dtype not in [np.float64, np.int64, float, int]:
            return {"error": f"Column '{column}' is not numeric"}

        percentiles = [10, 25, 50, 75, 90, 95, 99]
        values = {f"p{p}": round(float(series.quantile(p / 100)), 4) for p in percentiles}
        values["mean"] = round(float(series.mean()), 4)
        values["std"] = round(float(series.std()), 4)

        return values
