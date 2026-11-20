"""Build FastAPI routes from OpenAPI spec"""

from typing import Callable
from fastapi import Path
from .data_generator import DataGenerator
from .schema_resolver import SchemaResolver


class RouteBuilder:
    """Create FastAPI routes from OpenAPI spec"""

    def build_routes(self, app, spec, seed=None):
        """Add all routes from spec to FastAPI app"""
        paths = spec.get("paths", {})
        components = spec.get("components", {})
        generator = DataGenerator(seed=seed)

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch", "options", "head"]:
                    continue

                # Get responses
                responses = operation.get("responses", {})

                # Find first 2xx response
                response_schema = None
                response_code = None
                for code_str, response_obj in responses.items():
                    if code_str.startswith("2"):
                        response_code = int(code_str)
                        # Extract schema from response
                        content = response_obj.get("content", {})
                        json_content = content.get("application/json", {})
                        response_schema = json_content.get("schema")
                        break

                if response_schema is None:
                    continue

                # Get path parameters
                parameters = operation.get("parameters", [])
                path_params = {}
                for param in parameters:
                    if param.get("in") == "path":
                        param_name = param.get("name")
                        param_schema = param.get("schema", {})
                        path_params[param_name] = param_schema

                # Create route handler with dynamic signature
                handler = self._create_route_handler(
                    response_schema, path_params, generator, components, response_code
                )

                # Convert OpenAPI path to FastAPI path
                fastapi_path = self._normalize_path(path)

                # Register route
                app.add_api_route(
                    fastapi_path,
                    handler,
                    methods=[method.upper()],
                    status_code=response_code or 200
                )

    def _create_route_handler(self, schema, path_params, generator, components, response_code):
        """Create FastAPI route handler function with dynamic parameters"""
        # Build function signature dynamically
        if not path_params:
            # No path params - simple handler
            def handler():
                return generator.generate_from_schema(schema, components)
            return handler
        else:
            # With path params - use Path() dependencies
            def handler(**kwargs):
                data = generator.generate_from_schema(schema, components)

                # Inject path parameters into response if it's a dict
                if isinstance(data, dict):
                    for param_name, param_schema in path_params.items():
                        if param_name in kwargs:
                            param_value = kwargs[param_name]
                            if param_schema.get("type") == "integer":
                                try:
                                    param_value = int(param_value)
                                except (ValueError, TypeError):
                                    pass
                            data[param_name] = param_value

                return data

            # Add Path() annotations to function parameters
            handler.__signature__ = self._build_signature(path_params)
            return handler

    def _build_signature(self, path_params):
        """Build function signature with Path parameters"""
        import inspect
        params = []
        for param_name in path_params.keys():
            params.append(
                inspect.Parameter(
                    param_name,
                    inspect.Parameter.KEYWORD_ONLY,
                    annotation=int,
                    default=Path(...)
                )
            )
        return inspect.Signature(params)

    def _normalize_path(self, openapi_path):
        """Convert OpenAPI path syntax to FastAPI syntax (already compatible)"""
        # OpenAPI uses {id}, FastAPI also uses {id}, so no conversion needed
        return openapi_path
