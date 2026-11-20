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


class TestDataGeneratorFieldNames:
    """Tests for realistic field name generation"""

    def test_field_name_exact_match_generates_realistic_name(self):
        """Field 'name' exactly matched generates realistic person name"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}

        for _ in range(20):
            data = gen.generate_from_schema(schema, {})
            # Name pattern: First capital letter, letters/spaces/hyphens/apostrophes/dots
            assert re.match(r"^[A-Z][a-zA-Z\s'\-\.]*$", data["name"]), f"Invalid name: {data['name']}"

    def test_field_name_city_generates_realistic_city(self):
        """Field 'city' generates realistic city name"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"city": {"type": "string"}}}

        for _ in range(20):
            data = gen.generate_from_schema(schema, {})
            # City pattern: First capital letter, letters/spaces/hyphens/dots
            assert re.match(r"^[A-Z][a-zA-Z\s'\-\.]*$", data["city"]), f"Invalid city: {data['city']}"

    def test_field_name_street_must_contain_digit_and_space(self):
        """Field 'street' generates address with digit and space"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"street": {"type": "string"}}}

        for _ in range(20):
            data = gen.generate_from_schema(schema, {})
            # Street address must have both digit and space
            assert any(c.isdigit() for c in data["street"]), f"No digit in street: {data['street']}"
            assert " " in data["street"], f"No space in street: {data['street']}"

    def test_field_name_zipcode_valid_format(self):
        """Field 'zipcode' generates valid zipcode format"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"zipcode": {"type": "string"}}}

        for _ in range(20):
            data = gen.generate_from_schema(schema, {})
            # Zipcode: 5 digits, optionally +4 more after hyphen
            assert re.fullmatch(r"\d{5}(-\d{4})?", data["zipcode"]), f"Invalid zipcode: {data['zipcode']}"

    def test_field_name_phone_contains_digits(self):
        """Field 'phone' generates phone number with digits"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"phone": {"type": "string"}}}

        for _ in range(20):
            data = gen.generate_from_schema(schema, {})
            # Phone must contain digits
            assert any(c.isdigit() for c in data["phone"]), f"No digits in phone: {data['phone']}"

    def test_field_name_username_not_matched(self):
        """Field 'username' NOT matched by 'name' rule (exact match only)"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"username": {"type": "string"}}}

        for _ in range(20):
            data = gen.generate_from_schema(schema, {})
            # Username should be random lowercase (fallback), NOT a realistic name
            assert re.match(r"^[a-z]+$", data["username"]), f"Username should be random letters: {data['username']}"

    def test_format_takes_priority_over_field_name(self):
        """Format takes priority over field name matching"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"name": {"type": "string", "format": "email"}}}

        data = gen.generate_from_schema(schema, {})
        # Should be email format, not a person name
        assert re.match(r"^[^@]+@[^@]+\.[^@]+$", data["name"]), f"Should be email: {data['name']}"

    def test_enum_takes_priority_over_field_name(self):
        """Enum takes priority over field name matching"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"city": {"enum": ["red", "green", "blue"]}}}

        data = gen.generate_from_schema(schema, {})
        # Should pick from enum, not generate city
        assert data["city"] in ["red", "green", "blue"]

    def test_field_name_respects_maxLength_with_rstrip(self):
        """Field name generation respects maxLength and rstrips trailing spaces"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"name": {"type": "string", "maxLength": 10}}}

        for _ in range(20):
            data = gen.generate_from_schema(schema, {})
            # Must be <= maxLength after rstrip
            assert len(data["name"].rstrip()) <= 10, f"Too long after rstrip: {data['name']} ({len(data['name'])})"
            # But stored value should be <= maxLength (before rstrip)
            assert len(data["name"]) <= 10, f"Stored value too long: {data['name']} ({len(data['name'])})"

    def test_field_name_respects_minLength_not_broken_by_rstrip(self):
        """Field name generation respects minLength even after rstrip"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"name": {"type": "string", "minLength": 8, "maxLength": 15}}}

        for _ in range(20):
            data = gen.generate_from_schema(schema, {})
            # Must be >= minLength
            assert len(data["name"]) >= 8, f"Too short: {data['name']} ({len(data['name'])})"
            # Must be <= maxLength
            assert len(data["name"]) <= 15, f"Too long: {data['name']} ({len(data['name'])})"

    def test_multiple_field_names_in_object(self):
        """Multiple realistic field names in single object"""
        gen = DataGenerator(seed=42)
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "city": {"type": "string"},
                "phone": {"type": "string"}
            }
        }

        data = gen.generate_from_schema(schema, {})
        # Each should be realistic for its field
        assert re.match(r"^[A-Z][a-zA-Z\s'\-\.]*$", data["name"])
        assert re.match(r"^[A-Z][a-zA-Z\s'\-\.]*$", data["city"])
        assert any(c.isdigit() for c in data["phone"])

    def test_field_name_seed_reproducibility(self):
        """Field name generation respects seed"""
        gen1 = DataGenerator(seed=99)
        schema1 = {"type": "object", "properties": {"name": {"type": "string"}}}
        data1 = gen1.generate_from_schema(schema1, {})

        gen2 = DataGenerator(seed=99)
        schema2 = {"type": "object", "properties": {"name": {"type": "string"}}}
        data2 = gen2.generate_from_schema(schema2, {})

        assert data1["name"] == data2["name"], "Same seed should produce same name"

    def test_unknown_field_name_falls_back_to_random(self):
        """Unknown field name falls back to random string"""
        gen = DataGenerator(seed=42)
        schema = {"type": "object", "properties": {"xyz_unknown_field": {"type": "string"}}}

        for _ in range(20):
            data = gen.generate_from_schema(schema, {})
            # Unknown field → random lowercase letters
            assert re.match(r"^[a-z]+$", data["xyz_unknown_field"]), f"Should be random: {data['xyz_unknown_field']}"


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
