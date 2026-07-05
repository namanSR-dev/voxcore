"""
observability/metrics/metrics_registry.py

Centralized registry for recording system metrics (latency, token usage).
"""
from typing import Dict
from prometheus_client import Counter, Histogram

class MetricsRegistry:
    """
    Records statistical metrics for Prometheus or DataDog export.
    """
    def __init__(self) -> None:
        self._counters: Dict[str, Counter] = {}
        self._histograms: Dict[str, Histogram] = {}

    def increment_counter(self, name: str, tags: Dict[str, str]) -> None:
        """
        Increments a named counter.
        """
        if name not in self._counters:
            labelnames = list(tags.keys())
            self._counters[name] = Counter(name, f"Counter for {name}", labelnames=labelnames)
        
        self._counters[name].labels(**tags).inc()

    def record_histogram(self, name: str, value: float, tags: Dict[str, str]) -> None:
        """
        Records a value into a histogram (e.g., latency in ms).
        """
        if name not in self._histograms:
            labelnames = list(tags.keys())
            self._histograms[name] = Histogram(name, f"Histogram for {name}", labelnames=labelnames)
        
        self._histograms[name].labels(**tags).observe(value)
