"""
main.py

The ASGI entry point for the FastAPI server.
"""
from fastapi import FastAPI, Request
from voxcore.api.controllers.http_controller import HttpController
from voxcore.api.runtime_gateway import RuntimeGateway
from voxcore.api.exception_translator import ExceptionTranslator
from voxcore.runtime.pipeline.execution_pipeline import RuntimeExecutionPipeline

app = FastAPI(title="VoxCore API", version="1.0.0")

# Dependency Injection setup
# (In production, this would be handled by a DI container or the Bootstrapper)
class DummyRegistry:
    def get_provider(self, name):
        class DummyProvider:
            async def execute(self, req):
                from voxcore.contracts.runtime.models import Response
                return Response(id="res-123", request_id=req.id, output={"text": f"Mocked AI reply to: {req.payload['text']}"})
        return DummyProvider()

pipeline = RuntimeExecutionPipeline(context_builder=None, provider_registry=DummyRegistry())
gateway = RuntimeGateway(pipeline)
translator = ExceptionTranslator()
controller = HttpController(gateway, translator)

@app.get("/health")
async def health_check():
    """
    Load balancer health probe endpoint.
    """
    return await controller.health_check()

@app.post("/v1/inference")
async def execute_inference(request: Request):
    """
    Main entrypoint for conversational AI requests.
    """
    payload = await request.json()
    return await controller.accept_request(payload)
