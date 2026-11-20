import pytest
import re
from uuid import UUID
from datetime import datetime
from mockserver.data_generator import DataGenerator
from mockserver.errors import DataGenerationError


class TestDataGeneratorPrimitives:
    """Tests for primitive data types"""

    def test_generate_string(self):
        """Generate simple string"""
        gen = DataGenerator()
        schema = {"type": "string"}
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, str)

    def test_generate_integer(self):
        """Generate integer"""
        gen = DataGenerator()
        schema = {"type": "integer"}
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, int)

    def test_generate_number(self):
        """Generate float/number"""
        gen = DataGenerator()
        schema = {"type": "number"}
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, (int, float))

    def test_generate_boolean(self):
        """Generate boolean"""
        gen = DataGenerator()
        schema = {"type": "boolean"}
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, bool)


class TestDataGeneratorConstraints:
    """Tests for schema constraints"""

    def test_integer_minimum_constraint(self):
        """Generate integer respecting minimum"""
        gen = DataGenerator()
        schema = {"type": "integer", "minimum": 10}
        for _ in range(10):
            value = gen.generate_from_schema(schema, {})
            assert value >= 10

    def test_integer_maximum_constraint(self):
        """Generate integer respecting maximum"""
        gen = DataGenerator()
        schema = {"type": "integer", "maximum": 100}
        for _ in range(10):
            value = gen.generate_from_schema(schema, {})
            assert value <= 100

    def test_integer_min_max_range(self):
        """Generate integer within min/max range"""
        gen = DataGenerator()
        schema = {"type": "integer", "minimum": 50, "maximum": 60}
        for _ in range(10):
            value = gen.generate_from_schema(schema, {})
            assert 50 <= value <= 60

    def test_string_minLength_constraint(self):
        """Generate string respecting minLength"""
        gen = DataGenerator()
        schema = {"type": "string", "minLength": 5}
        for _ in range(10):
            value = gen.generate_from_schema(schema, {})
            assert len(value) >= 5

    def test_string_maxLength_constraint(self):
        """Generate string respecting maxLength"""
        gen = DataGenerator()
        schema = {"type": "string", "maxLength": 10}
        for _ in range(10):
            value = gen.generate_from_schema(schema, {})
            assert len(value) <= 10

    def test_string_length_range(self):
        """Generate string within minLength/maxLength range"""
        gen = DataGenerator()
        schema = {"type": "string", "minLength": 3, "maxLength": 7}
        for _ in range(10):
            value = gen.generate_from_schema(schema, {})
            assert 3 <= len(value) <= 7

    def test_array_minItems_constraint(self):
        """Generate array respecting minItems"""
        gen = DataGenerator()
        schema = {"type": "array", "minItems": 2, "items": {"type": "string"}}
        for _ in range(5):
            value = gen.generate_from_schema(schema, {})
            assert len(value) >= 2

    def test_array_maxItems_constraint(self):
        """Generate array respecting maxItems"""
        gen = DataGenerator()
        schema = {"type": "array", "maxItems": 3, "items": {"type": "string"}}
        for _ in range(5):
            value = gen.generate_from_schema(schema, {})
            assert len(value) <= 3

    def test_array_items_range(self):
        """Generate array within minItems/maxItems range"""
        gen = DataGenerator()
        schema = {"type": "array", "minItems": 2, "maxItems": 5, "items": {"type": "integer"}}
        for _ in range(5):
            value = gen.generate_from_schema(schema, {})
            assert 2 <= len(value) <= 5
            assert all(isinstance(item, int) for item in value)

    def test_enum_single_value(self):
        """Generate enum with single value"""
        gen = DataGenerator()
        schema = {"enum": ["only_value"]}
        value = gen.generate_from_schema(schema, {})
        assert value == "only_value"

    def test_enum_multiple_values(self):
        """Generate enum picking from multiple values"""
        gen = DataGenerator()
        schema = {"enum": ["available", "pending", "sold"]}
        for _ in range(10):
            value = gen.generate_from_schema(schema, {})
            assert value in ["available", "pending", "sold"]


class TestDataGeneratorFormats:
    """Tests for string formats"""

    def test_format_email(self):
        """Generate valid email"""
        gen = DataGenerator()
        schema = {"type": "string", "format": "email"}
        for _ in range(5):
            value = gen.generate_from_schema(schema, {})
            assert re.match(r'^[^@]+@[^@]+\.[^@]+$', value)

    def test_format_uuid(self):
        """Generate valid UUID"""
        gen = DataGenerator()
        schema = {"type": "string", "format": "uuid"}
        for _ in range(5):
            value = gen.generate_from_schema(schema, {})
            try:
                UUID(value)
                assert True
            except ValueError:
                pytest.fail(f"Invalid UUID: {value}")

    def test_format_date_time(self):
        """Generate valid date-time"""
        gen = DataGenerator()
        schema = {"type": "string", "format": "date-time"}
        for _ in range(5):
            value = gen.generate_from_schema(schema, {})
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                assert True
            except ValueError:
                pytest.fail(f"Invalid date-time: {value}")

    def test_format_date(self):
        """Generate valid date"""
        gen = DataGenerator()
        schema = {"type": "string", "format": "date"}
        for _ in range(5):
            value = gen.generate_from_schema(schema, {})
            try:
                datetime.strptime(value, '%Y-%m-%d')
                assert True
            except ValueError:
                pytest.fail(f"Invalid date: {value}")


class TestDataGeneratorObjects:
    """Tests for objects and nested schemas"""

    def test_generate_object_with_properties(self):
        """Generate object with properties"""
        gen = DataGenerator()
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, dict)
        assert "name" in value
        assert "age" in value

    def test_generate_object_required_fields(self):
        """Generate object with required fields"""
        gen = DataGenerator()
        schema = {
            "type": "object",
            "required": ["id", "name"],
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "optional": {"type": "string"}
            }
        }
        value = gen.generate_from_schema(schema, {})
        assert "id" in value
        assert "name" in value

    def test_generate_array_of_objects(self):
        """Generate array of objects"""
        gen = DataGenerator()
        schema = {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {"id": {"type": "integer"}}
            }
        }
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, list)
        assert len(value) >= 1
        assert all(isinstance(item, dict) for item in value)


class TestDataGeneratorReferences:
    """Tests for $ref resolution and nested schemas"""

    def test_resolve_simple_ref(self):
        """Resolve simple $ref"""
        gen = DataGenerator()
        schema = {"$ref": "#/components/schemas/Pet"}
        components = {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}}
                }
            }
        }
        value = gen.generate_from_schema(schema, components)
        assert isinstance(value, dict)
        assert "id" in value

    def test_nested_ref_two_levels(self):
        """Resolve two levels of nested $refs (Pet -> Owner)"""
        gen = DataGenerator()
        schema = {"$ref": "#/components/schemas/Pet"}
        components = {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "owner": {"$ref": "#/components/schemas/Owner"}
                    }
                },
                "Owner": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}}
                }
            }
        }
        value = gen.generate_from_schema(schema, components)
        assert isinstance(value, dict)
        assert "owner" in value
        assert isinstance(value["owner"], dict)
        assert "name" in value["owner"]

    def test_nested_ref_three_levels(self):
        """Resolve three levels of nested $refs (Pet -> Owner -> Address)"""
        gen = DataGenerator()
        schema = {"$ref": "#/components/schemas/Pet"}
        components = {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "owner": {"$ref": "#/components/schemas/Owner"}
                    }
                },
                "Owner": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "address": {"$ref": "#/components/schemas/Address"}
                    }
                },
                "Address": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}}
                }
            }
        }
        value = gen.generate_from_schema(schema, components)
        assert isinstance(value, dict)
        assert "owner" in value
        assert isinstance(value["owner"], dict)
        assert "address" in value["owner"]
        assert isinstance(value["owner"]["address"], dict)

    def test_circular_ref_not_infinite_loop(self):
        """Circular reference doesn't cause infinite loop (A -> B -> A), depth max 3"""
        gen = DataGenerator()
        schema = {"$ref": "#/components/schemas/NodeA"}
        components = {
            "schemas": {
                "NodeA": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "next": {"$ref": "#/components/schemas/NodeB"}
                    }
                },
                "NodeB": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "parent": {"$ref": "#/components/schemas/NodeA"}
                    }
                }
            }
        }
        value = gen.generate_from_schema(schema, components)
        assert isinstance(value, dict)
        # Level 1: NodeA is dict
        assert isinstance(value, dict)
        # Level 2: NodeA.next is NodeB (dict)
        assert isinstance(value["next"], dict)
        # Level 3: NodeB.parent is NodeA (dict)
        assert isinstance(value["next"]["parent"], dict)
        # Level 4: NodeA.next should be None (depth limit reached)
        assert value["next"]["parent"]["next"] is None

    def test_depth_limit_prevents_deep_nesting(self):
        """Depth limit (max 3 levels) prevents excessive nesting"""
        gen = DataGenerator()
        # Create a very deep schema: A -> B -> C -> D -> E
        schema = {"$ref": "#/components/schemas/LevelA"}
        components = {
            "schemas": {
                "LevelA": {
                    "type": "object",
                    "properties": {"ref": {"$ref": "#/components/schemas/LevelB"}}
                },
                "LevelB": {
                    "type": "object",
                    "properties": {"ref": {"$ref": "#/components/schemas/LevelC"}}
                },
                "LevelC": {
                    "type": "object",
                    "properties": {"ref": {"$ref": "#/components/schemas/LevelD"}}
                },
                "LevelD": {
                    "type": "object",
                    "properties": {"ref": {"$ref": "#/components/schemas/LevelE"}}
                },
                "LevelE": {
                    "type": "object",
                    "properties": {"value": {"type": "string"}}
                }
            }
        }
        value = gen.generate_from_schema(schema, components)
        # Level 1: LevelA is dict
        assert isinstance(value, dict)
        # Level 2: LevelA.ref is LevelB (dict)
        assert isinstance(value["ref"], dict)
        # Level 3: LevelB.ref is LevelC (dict)
        assert isinstance(value["ref"]["ref"], dict)
        # Level 4: Should stop - LevelC.ref should be None (depth limit reached)
        assert value["ref"]["ref"]["ref"] is None


class TestDataGeneratorSeed:
    """Tests for seed-based reproducibility"""

    def test_same_seed_produces_same_data(self):
        """Same seed produces identical data"""
        schema = {"type": "string"}

        gen1 = DataGenerator(seed=42)
        value1 = gen1.generate_from_schema(schema, {})

        gen2 = DataGenerator(seed=42)
        value2 = gen2.generate_from_schema(schema, {})

        assert value1 == value2

    def test_different_seed_produces_different_data(self):
        """Different seeds produce different data"""
        schema = {"type": "integer"}

        gen1 = DataGenerator(seed=42)
        value1 = gen1.generate_from_schema(schema, {})

        gen2 = DataGenerator(seed=99)
        value2 = gen2.generate_from_schema(schema, {})

        # Different seeds usually produce different values (not guaranteed but very likely)
        # We test multiple generations to ensure variability
        assert value1 != value2

    def test_seed_consistent_across_multiple_calls(self):
        """Same seed produces consistent data across multiple generations"""
        gen1 = DataGenerator(seed=123)
        values1 = [gen1.generate_from_schema({"type": "string"}, {}) for _ in range(5)]

        gen2 = DataGenerator(seed=123)
        values2 = [gen2.generate_from_schema({"type": "string"}, {}) for _ in range(5)]

        assert values1 == values2

    def test_seed_with_complex_schema(self):
        """Seed works with complex nested schemas"""
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "minimum": 1, "maximum": 1000},
                "name": {"type": "string"},
                "status": {"enum": ["active", "inactive"]}
            }
        }

        gen1 = DataGenerator(seed=555)
        value1 = gen1.generate_from_schema(schema, {})

        gen2 = DataGenerator(seed=555)
        value2 = gen2.generate_from_schema(schema, {})

        assert value1 == value2

    def test_seed_independent_generators(self):
        """Two generators with same seed produce same values independently"""
        schema = {"type": "integer", "minimum": 1, "maximum": 1000}

        gen1 = DataGenerator(seed=42)
        gen2 = DataGenerator(seed=42)

        # Both generators should produce same sequence independently
        v1_1 = gen1.generate_from_schema(schema, {})
        v2_1 = gen2.generate_from_schema(schema, {})
        assert v1_1 == v2_1, "First values from two generators with same seed should match"

        v1_2 = gen1.generate_from_schema(schema, {})
        v2_2 = gen2.generate_from_schema(schema, {})
        assert v1_2 == v2_2, "Second values from two generators with same seed should match"


class TestDataGeneratorBugFixes:
    """Regression tests for edge cases and bugs"""

    def test_string_minLength_without_maxLength(self):
        """Regression: minLength without maxLength should not fail"""
        gen = DataGenerator()
        schema = {"type": "string", "minLength": 30}
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, str)
        assert len(value) >= 30

    def test_integer_minimum_without_maximum(self):
        """Regression: minimum without maximum should not fail"""
        gen = DataGenerator()
        schema = {"type": "integer", "minimum": 5000}
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, int)
        assert value >= 5000

    def test_array_minItems_without_maxItems(self):
        """Regression: minItems without maxItems should not fail"""
        gen = DataGenerator()
        schema = {"type": "array", "minItems": 15, "items": {"type": "string"}}
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, list)
        assert len(value) >= 15

    def test_integer_maximum_without_minimum(self):
        """Regression: maximum < default minimum should not fail"""
        gen = DataGenerator()
        schema = {"type": "integer", "maximum": -5000}
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, int)
        assert value <= -5000

    def test_string_maxLength_zero(self):
        """Regression: maxLength=0 (edge case) should not fail"""
        gen = DataGenerator()
        schema = {"type": "string", "maxLength": 0}
        value = gen.generate_from_schema(schema, {})
        assert isinstance(value, str)
        assert len(value) == 0
