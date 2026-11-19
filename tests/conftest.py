import pytest
import yaml
from pathlib import Path


@pytest.fixture
def petstore_spec():
    """Load petstore.yaml example spec"""
    spec_path = Path(__file__).parent / "fixtures" / "petstore.yaml"
    with open(spec_path, "r") as f:
        return yaml.safe_load(f)


@pytest.fixture
def simple_valid_spec():
    """Minimal valid OpenAPI 3.0 spec"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0"
        },
        "paths": {
            "/test": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def spec_without_openapi():
    """Spec missing openapi field"""
    return {
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {}
    }


@pytest.fixture
def spec_wrong_version():
    """Spec with Swagger 2.0 version"""
    return {
        "swagger": "2.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {}
    }
