from .errors import SchemaResolveError


class SchemaResolver:
    """Resolve $ref references in schemas"""

    def resolve(self, ref: str, components: dict) -> dict:
        """Resolve $ref to actual schema"""
        if not ref.startswith("#/"):
            raise SchemaResolveError(f"Invalid $ref format: {ref}")

        if "schemas" not in components:
            raise SchemaResolveError("Missing 'schemas' in components")

        # Parse ref: #/components/schemas/Pet
        parts = ref.split("/")
        if (len(parts) < 4 or parts[0] != "#" or
            parts[1] != "components" or parts[2] != "schemas"):
            raise SchemaResolveError(f"Invalid $ref format: {ref}")

        schema_name = parts[3]
        return self.get_schema(schema_name, components)

    def get_schema(self, schema_name: str, components: dict) -> dict:
        """Get schema by name from components"""
        if "schemas" not in components:
            raise SchemaResolveError("Missing 'schemas' in components")

        schemas = components["schemas"]
        if schema_name not in schemas:
            raise SchemaResolveError(f"Schema not found: {schema_name}")

        return schemas[schema_name]

    def collect_all_refs(self, schema: dict, components: dict) -> set:
        """Collect all $refs in a schema"""
        refs = set()

        def traverse(obj):
            if isinstance(obj, dict):
                if "$ref" in obj:
                    refs.add(obj["$ref"])
                for value in obj.values():
                    traverse(value)
            elif isinstance(obj, list):
                for item in obj:
                    traverse(item)

        traverse(schema)
        return refs
