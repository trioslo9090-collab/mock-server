import json
import yaml
from pathlib import Path
from .errors import SpecLoadError


class SpecLoader:
    """Parse and extract OpenAPI 3 specification"""

    def load_spec(self, file_path: str) -> dict:
        """Load and parse spec file (YAML or JSON)"""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Spec file not found: {file_path}")

            content = path.read_text()

            if path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(content)
            elif path.suffix.lower() == '.json':
                return json.loads(content)
            else:
                # Try YAML first, then JSON
                try:
                    return yaml.safe_load(content)
                except yaml.YAMLError:
                    return json.loads(content)
        except FileNotFoundError as e:
            raise SpecLoadError(str(e))
        except yaml.YAMLError as e:
            raise SpecLoadError(f"Invalid YAML: {e}")
        except json.JSONDecodeError as e:
            raise SpecLoadError(f"Invalid JSON: {e}")
        except Exception as e:
            raise SpecLoadError(f"Error loading spec: {e}")

    def validate_structure(self, spec: dict) -> bool:
        """Validate OpenAPI 3.x structure"""
        if "openapi" not in spec:
            raise SpecLoadError("Missing 'openapi' field")

        openapi_version = spec["openapi"]
        if not isinstance(openapi_version, str) or not openapi_version.startswith("3."):
            raise SpecLoadError(f"OpenAPI version must be 3.x, got: {openapi_version}")

        if "info" not in spec:
            raise SpecLoadError("Missing 'info' field")

        info = spec["info"]
        if not isinstance(info, dict) or "title" not in info:
            raise SpecLoadError("Missing 'info.title' field")

        if "paths" not in spec:
            raise SpecLoadError("Missing 'paths' field")

        if not isinstance(spec["paths"], dict):
            raise SpecLoadError("'paths' must be an object")

        return True

    def get_paths(self, spec: dict) -> dict:
        """Extract all paths from spec"""
        self.validate_structure(spec)
        return spec.get("paths", {})

    def get_components(self, spec: dict) -> dict:
        """Extract components from spec"""
        self.validate_structure(spec)
        return spec.get("components", {})

    def get_path_item(self, spec: dict, path: str) -> dict:
        """Get specific path item"""
        self.validate_structure(spec)
        paths = spec.get("paths", {})
        if path not in paths:
            raise SpecLoadError(f"Path not found: {path}")
        return paths[path]
