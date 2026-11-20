"""FastAPI app factory"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .spec_loader import SpecLoader
from .route_builder import RouteBuilder


def create_app(spec, seed=None):
    """Create FastAPI app from OpenAPI spec"""
    app = FastAPI()

    # Register routes from spec
    builder = RouteBuilder()
    builder.build_routes(app, spec, seed)

    # 404 handler
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"error": f"Route not found: {request.url.path}"}
        )

    return app
