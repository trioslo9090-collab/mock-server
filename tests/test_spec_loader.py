import pytest
import yaml
from pathlib import Path
from mockserver.spec_loader import SpecLoader
from mockserver.errors import SpecLoadError


class TestSpecLoader:
    """Tests for SpecLoader class"""

    def test_load_valid_yaml_spec(self, tmp_path):
        """Test loading a valid YAML spec file"""
        spec_file = tmp_path / "valid.yaml"
        spec_content = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {}
        }
        spec_file.write_text(yaml.dump(spec_content))

        loader = SpecLoader()
        spec = loader.load_spec(str(spec_file))

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test"

    def test_load_valid_json_spec(self, tmp_path):
        """Test loading a valid JSON spec file"""
        import json
        spec_file = tmp_path / "valid.json"
        spec_content = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {}
        }
        spec_file.write_text(json.dumps(spec_content))

        loader = SpecLoader()
        spec = loader.load_spec(str(spec_file))

        assert spec["openapi"] == "3.0.0"

    def test_load_petstore_spec(self, petstore_spec):
        """Test loading petstore example spec"""
        loader = SpecLoader()
        # petstore_spec is already loaded from conftest
        assert loader.validate_structure(petstore_spec) is True

    def test_error_file_not_found(self):
        """Test error on missing file"""
        loader = SpecLoader()
        with pytest.raises(SpecLoadError):
            loader.load_spec("/nonexistent/path/spec.yaml")

    def test_error_invalid_yaml(self, tmp_path):
        """Test error on invalid YAML"""
        spec_file = tmp_path / "invalid.yaml"
        spec_file.write_text("{ invalid: yaml: content:")

        loader = SpecLoader()
        with pytest.raises(SpecLoadError):
            loader.load_spec(str(spec_file))

    def test_validate_missing_openapi_field(self, spec_without_openapi):
        """Test validation fails without openapi field"""
        loader = SpecLoader()
        with pytest.raises(SpecLoadError):
            loader.validate_structure(spec_without_openapi)

    def test_validate_wrong_version(self, spec_wrong_version):
        """Test validation fails with non-3.x version"""
        loader = SpecLoader()
        with pytest.raises(SpecLoadError):
            loader.validate_structure(spec_wrong_version)

    def test_validate_missing_info(self):
        """Test validation fails without info field"""
        loader = SpecLoader()
        spec = {"openapi": "3.0.0", "paths": {}}
        with pytest.raises(SpecLoadError):
            loader.validate_structure(spec)

    def test_validate_missing_paths(self):
        """Test validation fails without paths field"""
        loader = SpecLoader()
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"}
        }
        with pytest.raises(SpecLoadError):
            loader.validate_structure(spec)

    def test_get_paths_from_spec(self, petstore_spec):
        """Test extracting paths from spec"""
        loader = SpecLoader()
        paths = loader.get_paths(petstore_spec)

        assert "/pets" in paths
        assert "/pets/{id}" in paths
        assert "get" in paths["/pets"]
        assert "post" in paths["/pets"]

    def test_get_components_from_spec(self, petstore_spec):
        """Test extracting components from spec"""
        loader = SpecLoader()
        components = loader.get_components(petstore_spec)

        assert "schemas" in components
        assert "Pet" in components["schemas"]
        assert "Owner" in components["schemas"]
        assert "Address" in components["schemas"]

    def test_get_path_item(self, petstore_spec):
        """Test extracting specific path item"""
        loader = SpecLoader()
        path_item = loader.get_path_item(petstore_spec, "/pets")

        assert "get" in path_item
        assert "post" in path_item

    def test_valid_spec_structure(self, simple_valid_spec):
        """Test validation succeeds with valid spec"""
        loader = SpecLoader()
        result = loader.validate_structure(simple_valid_spec)
        assert result is True
