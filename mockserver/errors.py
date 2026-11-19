"""Custom exception classes for mock server"""


class MockServerError(Exception):
    """Base exception for mock server errors"""
    pass


class SpecLoadError(MockServerError):
    """Error loading or parsing OpenAPI spec"""
    pass


class SchemaResolveError(MockServerError):
    """Error resolving $ref in schema"""
    pass


class DataGenerationError(MockServerError):
    """Error generating mock data"""
    pass
