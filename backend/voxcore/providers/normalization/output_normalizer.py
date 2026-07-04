"""
providers/normalization/output_normalizer.py

Normalizes vendor-specific payload structures into universal domain models.
"""
from typing import Dict, Any

class OutputNormalizer:
    """
    Standardizes output payloads so the Runtime Package doesn't have to deal with vendor quirks.
    """
    def __init__(self) -> None:
        pass

    def normalize(self, raw_response: Dict[str, Any], provider_type: str) -> Any:
        """
        Converts a vendor response into a standard VoxCore Response struct.
        """
        pass

    def _parse_openai(self, raw: Dict[str, Any]) -> Any:
        pass

    def _parse_anthropic(self, raw: Dict[str, Any]) -> Any:
        pass
