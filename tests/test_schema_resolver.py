import pytest
from mockserver.schema_resolver import SchemaResolver
from mockserver.errors import SchemaResolveError


class TestSchemaResolver:
    """Tests for SchemaResolver class"""

    def test_resolve_simple_ref(self):
        """Test resolving a simple $ref"""
        resolver = SchemaResolver()
        components = {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}}
                }
            }
        }
        schema = resolver.resolve("#/components/schemas/Pet", components)
        assert schema["type"] == "object"
        assert "name" in schema["properties"]

    def test_resolve_ref_missing_schema(self):
        """Test error when ref target doesn't exist"""
        resolver = SchemaResolver()
        components = {"schemas": {}}
        with pytest.raises(SchemaResolveError):
            resolver.resolve("#/components/schemas/NonExistent", components)

    def test_resolve_nested_ref_in_properties(self):
        """Test resolving nested $ref in object properties"""
        resolver = SchemaResolver()
        components = {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "properties": {
                        "owner": {"$ref": "#/components/schemas/Owner"}
                    }
                },
                "Owner": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}}
                }
            }
        }
        pet_schema = resolver.resolve("#/components/schemas/Pet", components)
        owner_ref = pet_schema["properties"]["owner"]["$ref"]
        owner_schema = resolver.resolve(owner_ref, components)
        assert owner_schema["properties"]["name"]["type"] == "string"

    def test_resolve_ref_in_array_items(self):
        """Test resolving $ref in array items"""
        resolver = SchemaResolver()
        components = {
            "schemas": {
                "Pet": {"type": "object", "properties": {"id": {"type": "integer"}}},
            }
        }
        array_schema = {
            "type": "array",
            "items": {"$ref": "#/components/schemas/Pet"}
        }
        pet_ref = array_schema["items"]["$ref"]
        pet_schema = resolver.resolve(pet_ref, components)
        assert pet_schema["type"] == "object"

    def test_resolve_three_level_nested_refs(self):
        """Test resolving three levels of nested refs"""
        resolver = SchemaResolver()
        components = {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "properties": {"owner": {"$ref": "#/components/schemas/Owner"}}
                },
                "Owner": {
                    "type": "object",
                    "properties": {"address": {"$ref": "#/components/schemas/Address"}}
                },
                "Address": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}}
                }
            }
        }
        pet_schema = resolver.resolve("#/components/schemas/Pet", components)
        owner_ref = pet_schema["properties"]["owner"]["$ref"]
        owner_schema = resolver.resolve(owner_ref, components)
        address_ref = owner_schema["properties"]["address"]["$ref"]
        address_schema = resolver.resolve(address_ref, components)
        assert address_schema["properties"]["city"]["type"] == "string"

    def test_get_schema_by_name(self):
        """Test getting schema by name"""
        resolver = SchemaResolver()
        components = {
            "schemas": {
                "Pet": {"type": "object"}
            }
        }
        schema = resolver.get_schema("Pet", components)
        assert schema["type"] == "object"

    def test_get_schema_not_found(self):
        """Test error when getting non-existent schema"""
        resolver = SchemaResolver()
        components = {"schemas": {}}
        with pytest.raises(SchemaResolveError):
            resolver.get_schema("NonExistent", components)

    def test_collect_all_refs_in_schema(self):
        """Test collecting all refs from a schema"""
        resolver = SchemaResolver()
        components = {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "properties": {
                        "owner": {"$ref": "#/components/schemas/Owner"},
                        "tags": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Tag"}
                        }
                    }
                },
                "Owner": {"type": "object"},
                "Tag": {"type": "object"}
            }
        }
        pet_schema = resolver.resolve("#/components/schemas/Pet", components)
        refs = resolver.collect_all_refs(pet_schema, components)
        assert "#/components/schemas/Owner" in refs
        assert "#/components/schemas/Tag" in refs

    def test_resolve_invalid_ref_format(self):
        """Test error on invalid $ref format"""
        resolver = SchemaResolver()
        components = {"schemas": {}}
        with pytest.raises(SchemaResolveError):
            resolver.resolve("invalid-ref", components)

    def test_resolve_ref_missing_components(self):
        """Test error when components is missing schemas"""
        resolver = SchemaResolver()
        components = {}
        with pytest.raises(SchemaResolveError):
            resolver.resolve("#/components/schemas/Pet", components)
