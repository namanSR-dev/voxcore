"""
providers/normalization/output_normalizer.py

Normalizes vendor-specific payload structures into universal domain models.
"""
from typing import Dict, Any
from voxcore.contracts.runtime.models import Response

class OutputNormalizer:
    """
    Standardizes output payloads so the Runtime Package doesn't have to deal with vendor quirks.
    """
    def __init__(self) -> None:
        pass

    def normalize(self, raw_response: Dict[str, Any], provider_type: str) -> Response:
        """
        Converts a vendor response into a standard VoxCore Response struct.
        """
        if provider_type == "openai":
            return self._parse_openai(raw_response)
        elif provider_type == "ollama":
            return self._parse_ollama(raw_response)
        raise ValueError(f"Unknown provider type: {provider_type}")

    def _parse_openai(self, raw: Dict[str, Any]) -> Response:
        content = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
        return Response(id=raw.get("id", "openai-res"), request_id="", output={"text": content})

    def _parse_ollama(self, raw: Dict[str, Any]) -> Response:
        content = raw.get("message", {}).get("content", "")
        return Response(id="ollama-res", request_id="", output={"text": content})
