"""
observability/audit/audit_logger.py

Records security and access events for compliance purposes.
"""
from voxcore.observability.logging.structured_logger import StructuredLogger

class AuditLogger:
    """
    Dedicated logger for recording immutable audit trails.
    """
    def __init__(self, logger: StructuredLogger) -> None:
        self._logger = logger

    def log_access(self, identity: str, resource: str, action: str) -> None:
        """
        Records a security event.
        """
        self._logger.info(
            "AUDIT_EVENT",
            audit=True,
            identity=identity,
            resource=resource,
            action=action
        )
