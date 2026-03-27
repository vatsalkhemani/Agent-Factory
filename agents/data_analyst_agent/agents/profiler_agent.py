"""Profiler agent -- wraps the deterministic toolkit.profile() call.
No LLM needed for profiling; this is pure computation."""

from toolkit import AnalysisToolkit
from models import DataProfile


def profile_data(toolkit: AnalysisToolkit) -> DataProfile:
    return toolkit.profile()
