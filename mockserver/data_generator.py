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

        if seed is not None:
            random.seed(seed)
            self.faker = Faker()
            self.faker.seed_instance(seed)
        else:
            self.faker = Faker()

    def generate_from_schema(self, schema, components):
        """Generate data from schema"""
        return self._generate(schema, components, depth=0)

    def _generate(self, schema, components, depth=0):
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
            return random.choice(schema["enum"])

        # Handle by type
        schema_type = schema.get("type")

        if schema_type == "string":
            return self._generate_string(schema)
        elif schema_type == "integer":
            return self._generate_integer(schema)
        elif schema_type == "number":
            return self._generate_number(schema)
        elif schema_type == "boolean":
            return random.choice([True, False])
        elif schema_type == "array":
            return self._generate_array(schema, components, depth)
        elif schema_type == "object":
            return self._generate_object(schema, components, depth)

        return None

    def _generate_string(self, schema):
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

            length = random.randint(min_length, max_length)
            # Generate random string of exact length
            chars = "abcdefghijklmnopqrstuvwxyz"
            return "".join(random.choice(chars) for _ in range(length))

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

        return random.randint(minimum, maximum)

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

        return random.uniform(minimum, maximum)

    def _generate_array(self, schema, components, depth):
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
        count = random.randint(min_items, max_items)
        return [self._generate(items_schema, components, depth) for _ in range(count)]

    def _generate_object(self, schema, components, depth):
        """Generate object from properties"""
        properties = schema.get("properties", {})
        obj = {}

        for prop_name, prop_schema in properties.items():
            obj[prop_name] = self._generate(prop_schema, components, depth)

        return obj
