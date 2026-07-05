"""
observability/tracing/trace_context.py

Manages Distributed Tracing IDs across asynchronous boundaries.
"""
from typing import Dict, Any
import uuid

class TraceContext:
    """
    Coordinates trace spans to map the lifecycle of a request.
    """
    def __init__(self) -> None:
        self.trace_id = str(uuid.uuid4())
        self.current_span_id: str | None = None

    def start_span(self, name: str) -> Any:
        """
        Starts a new trace span. Returns the span ID.
        """
        self.current_span_id = str(uuid.uuid4())
        return self.current_span_id

    def inject(self, headers: Dict[str, str]) -> None:
        """
        Injects the current trace context into HTTP headers.
        """
        headers["X-Trace-Id"] = self.trace_id
        if self.current_span_id:
            headers["X-Span-Id"] = self.current_span_id
