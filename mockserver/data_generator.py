import random
from faker import Faker
from .schema_resolver import SchemaResolver


class DataGenerator:
    """Generate realistic mock data from JSON schemas"""

    MAX_DEPTH = 3

    def __init__(self, seed=None):
        """Initialize generator with optional seed for reproducibility"""
        self.seed = seed
        self.resolver = SchemaResolver()

        # Use independent random.Random instance instead of global random
        self.random = random.Random(seed)

        if seed is not None:
            self.faker = Faker()
            self.faker.seed_instance(seed)
        else:
            self.faker = Faker()

    def generate_from_schema(self, schema, components):
        """Generate data from schema"""
        return self._generate(schema, components, depth=0, field_name=None)

    def _generate(self, schema, components, depth=0, field_name=None):
        """Internal recursive generator with depth tracking"""
        if not isinstance(schema, dict):
            return None

        # Handle $ref: resolve and recurse
        if "$ref" in schema:
            if depth >= self.MAX_DEPTH:
                return None
            ref = schema["$ref"]
            resolved_schema = self.resolver.resolve(ref, components)
            return self._generate(resolved_schema, components, depth + 1)

        # Handle enum: pick random value
        if "enum" in schema:
            return self.random.choice(schema["enum"])

        # Handle by type
        schema_type = schema.get("type")

        if schema_type == "string":
            return self._generate_string(schema, field_name=field_name)
        elif schema_type == "integer":
            return self._generate_integer(schema)
        elif schema_type == "number":
            return self._generate_number(schema)
        elif schema_type == "boolean":
            return self.random.choice([True, False])
        elif schema_type == "array":
            return self._generate_array(schema, components, depth, field_name=field_name)
        elif schema_type == "object":
            return self._generate_object(schema, components, depth, field_name=field_name)

        return None

    def _generate_string(self, schema, field_name=None):
        """Generate string with format and length constraints"""
        fmt = schema.get("format")

        if fmt == "email":
            return self.faker.email()
        elif fmt == "uuid":
            return self.faker.uuid4()
        elif fmt == "date-time":
            dt = self.faker.date_time()
            return dt.isoformat()
        elif fmt == "date":
            return self.faker.date()
        else:
            # Plain string with length constraints
            # Never change schema values, only adapt defaults
            min_length = schema.get("minLength")
            max_length = schema.get("maxLength")

            if min_length is None:
                # min not in schema: use default, but respect max if present
                min_length = 1 if max_length is None else min(1, max_length)
            if max_length is None:
                # max not in schema: use default, but respect min
                max_length = max(20, min_length + 10)

            # Try field-name-based generation
            if field_name:
                return self._generate_string_by_field_name(field_name, min_length, max_length)

            # Fallback: random string
            return self._generate_random_string(min_length, max_length)

    def _generate_integer(self, schema):
        """Generate integer with min/max constraints"""
        # Never change schema values, only adapt defaults
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")

        if minimum is None:
            # min not in schema: use default, but respect max if present
            minimum = -1000 if maximum is None else min(-1000, maximum)
        if maximum is None:
            # max not in schema: use default, but respect min
            maximum = max(1000, minimum + 2000)

        return self.random.randint(minimum, maximum)

    def _generate_number(self, schema):
        """Generate float with min/max constraints"""
        # Never change schema values, only adapt defaults
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")

        if minimum is None:
            # min not in schema: use default, but respect max if present
            minimum = -1000.0 if maximum is None else min(-1000.0, maximum)
        if maximum is None:
            # max not in schema: use default, but respect min
            maximum = max(1000.0, minimum + 2000.0)

        return self.random.uniform(minimum, maximum)

    def _generate_array(self, schema, components, depth, field_name=None):
        """Generate array with minItems/maxItems constraints"""
        # Never change schema values, only adapt defaults
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")

        if min_items is None:
            # min not in schema: use default, but respect max if present
            min_items = 1 if max_items is None else min(1, max_items)
        if max_items is None:
            # max not in schema: use default, but respect min
            max_items = max(10, min_items + 5)

        items_schema = schema.get("items", {})
        count = self.random.randint(min_items, max_items)
        return [self._generate(items_schema, components, depth, field_name=None) for _ in range(count)]

    def _generate_object(self, schema, components, depth, field_name=None):
        """Generate object from properties"""
        properties = schema.get("properties", {})
        obj = {}

        for prop_name, prop_schema in properties.items():
            obj[prop_name] = self._generate(prop_schema, components, depth, field_name=prop_name)

        return obj

    def _generate_string_by_field_name(self, field_name, min_length, max_length):
        """Generate realistic string based on field name (exact match, lowercase)"""
        field_lower = field_name.lower()

        # Exact field name mappings
        field_map = {
            "name": lambda: self.faker.name(),
            "first_name": lambda: self.faker.first_name(),
            "last_name": lambda: self.faker.last_name(),
            "city": lambda: self.faker.city(),
            "street": lambda: self.faker.street_address(),
            "address_line": lambda: self.faker.street_address(),
            "zipcode": lambda: self.faker.zipcode(),
            "postcode": lambda: self.faker.postcode(),
            "zip": lambda: self.faker.postcode(),
            "phone": lambda: self.faker.phone_number(),
            "country": lambda: self.faker.country(),
            "company": lambda: self.faker.company(),
            "description": lambda: self.faker.sentence(),
            "title": lambda: self.faker.sentence(),
        }

        # Exact match only
        if field_lower in field_map:
            value = field_map[field_lower]()
            # Handle length constraints with rstrip
            if len(value) > max_length:
                value = value[:max_length].rstrip()
                # If rstrip made it too short, regenerate or pad
                if len(value) < min_length:
                    value = value[:max_length]  # Keep original truncation
            elif len(value) < min_length:
                # Pad with generated content
                extra = self._generate_random_string(min_length - len(value), min_length - len(value))
                value = (value + " " + extra)[:max_length]

            return value

        # Unknown field: random
        return self._generate_random_string(min_length, max_length)

    def _generate_random_string(self, min_length, max_length):
        """Generate random lowercase string"""
        length = self.random.randint(min_length, max_length)
        chars = "abcdefghijklmnopqrstuvwxyz"
        return "".join(self.random.choice(chars) for _ in range(length))
