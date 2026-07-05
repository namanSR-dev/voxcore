"""
api/controllers/http_controller.py

Receives HTTP REST requests, orchestrates validation, delegates mapping to adapters, 
and hands off execution to the runtime gateway. Connects HTTP 4xx/5xx responses.
"""
from typing import Dict, Any
from voxcore.api.runtime_gateway import RuntimeGateway
from voxcore.api.exception_translator import ExceptionTranslator
from voxcore.api.validation.schema_validator import SchemaValidator
from voxcore.api.adapters.request_adapter import RequestAdapter
from voxcore.api.adapters.response_adapter import ResponseAdapter

class HttpController:
    """
    HTTP route handler that isolates transport concerns from the VoxCore runtime.
    """
    def __init__(self, gateway: RuntimeGateway, translator: ExceptionTranslator) -> None:
        self.gateway = gateway
        self.translator = translator
        self.validator = SchemaValidator()
        self.req_adapter = RequestAdapter()
        self.res_adapter = ResponseAdapter()

    async def accept_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.validator.validate_request(payload)
            domain_req = self.req_adapter.to_domain(payload)
            domain_res = await self.gateway.submit_request(domain_req)
            return self.res_adapter.to_dto(domain_res)
        except Exception as e:
            return self.translator.translate(e)

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "version": "1.0.0"}

    def _extract_headers(self, raw_headers: Dict[str, str]) -> Dict[str, str]:
        return raw_headers
