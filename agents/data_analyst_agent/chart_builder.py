import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config import MAX_CHART_POINTS
from models import ChartSpec


def build_chart(df: pd.DataFrame, spec: ChartSpec) -> go.Figure | None:
    """Build a Plotly figure from a ChartSpec. Returns None if spec is invalid."""
    builders = {
        "bar": _build_bar,
        "scatter": _build_scatter,
        "line": _build_line,
        "histogram": _build_histogram,
        "box": _build_box,
        "heatmap": _build_heatmap,
        "pie": _build_pie,
    }
    builder = builders.get(spec.chart_type)
    if not builder:
        return None
    try:
        fig = builder(df, spec)
        if fig:
            fig.update_layout(
                title=spec.title,
                template="plotly_white",
                margin=dict(l=40, r=40, t=60, b=40),
            )
        return fig
    except Exception as e:
        print(f"Chart build failed for '{spec.title}': {e}")
        return None


def _safe_df(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Get a subset of the dataframe with valid columns, capped for rendering."""
    valid_cols = [c for c in cols if c in df.columns]
    if not valid_cols:
        return pd.DataFrame()
    subset = df[valid_cols].dropna(subset=valid_cols)
    if len(subset) > MAX_CHART_POINTS:
        subset = subset.sample(MAX_CHART_POINTS, random_state=42)
    return subset


def _build_bar(df: pd.DataFrame, spec: ChartSpec) -> go.Figure | None:
    if not spec.x_column or not spec.y_column:
        return None
    cols = [spec.x_column, spec.y_column]
    if spec.color_column:
        cols.append(spec.color_column)
    subset = _safe_df(df, cols)
    if subset.empty:
        return None

    # If x is categorical with many values, aggregate
    if subset[spec.x_column].dtype == object and subset[spec.x_column].nunique() > 20:
        agg = subset.groupby(spec.x_column)[spec.y_column].mean().nlargest(20).reset_index()
        return px.bar(agg, x=spec.x_column, y=spec.y_column, title=spec.title)

    return px.bar(subset, x=spec.x_column, y=spec.y_column,
                  color=spec.color_column, title=spec.title)


def _build_scatter(df: pd.DataFrame, spec: ChartSpec) -> go.Figure | None:
    if not spec.x_column or not spec.y_column:
        return None
    cols = [spec.x_column, spec.y_column]
    if spec.color_column:
        cols.append(spec.color_column)
    subset = _safe_df(df, cols)
    if subset.empty:
        return None
    return px.scatter(subset, x=spec.x_column, y=spec.y_column,
                      color=spec.color_column, title=spec.title)


def _build_line(df: pd.DataFrame, spec: ChartSpec) -> go.Figure | None:
    if not spec.x_column or not spec.y_column:
        return None
    cols = [spec.x_column, spec.y_column]
    if spec.color_column:
        cols.append(spec.color_column)
    subset = _safe_df(df, cols)
    if subset.empty:
        return None
    # Sort by x for line charts
    subset = subset.sort_values(spec.x_column)
    return px.line(subset, x=spec.x_column, y=spec.y_column,
                   color=spec.color_column, title=spec.title)


def _build_histogram(df: pd.DataFrame, spec: ChartSpec) -> go.Figure | None:
    col = spec.x_column or spec.y_column
    if not col:
        return None
    subset = _safe_df(df, [col])
    if subset.empty:
        return None
    nbins = spec.params.get("bins", 30)
    return px.histogram(subset, x=col, nbins=nbins, title=spec.title)


def _build_box(df: pd.DataFrame, spec: ChartSpec) -> go.Figure | None:
    y_col = spec.y_column or spec.x_column
    if not y_col:
        return None
    cols = [y_col]
    if spec.x_column and spec.x_column != y_col:
        cols.append(spec.x_column)
    subset = _safe_df(df, cols)
    if subset.empty:
        return None
    return px.box(subset, x=spec.x_column if spec.x_column != y_col else None,
                  y=y_col, title=spec.title)


def _build_heatmap(df: pd.DataFrame, spec: ChartSpec) -> go.Figure | None:
    """Build correlation heatmap for numeric columns."""
    numeric_cols = list(df.select_dtypes(include=[np.number]).columns)[:10]
    if len(numeric_cols) < 2:
        return None
    corr = df[numeric_cols].corr()
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto", title=spec.title,
        color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
    )
    return fig


def _build_pie(df: pd.DataFrame, spec: ChartSpec) -> go.Figure | None:
    col = spec.x_column
    if not col:
        return None
    vc = df[col].value_counts().head(10)
    fig = px.pie(values=vc.values, names=vc.index, title=spec.title)
    return fig
