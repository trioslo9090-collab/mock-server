# Mock Server for OpenAPI 3

Local mock server that parses OpenAPI 3 specifications and serves realistic random data for all endpoints. Useful for testing, development, and frontend integration without backend dependencies.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Quick Start

```bash
python -m mockserver tests/fixtures/petstore.yaml --port 8000 --seed 42
```

Then visit:
- `http://localhost:8000/pets` — GET array of pets
- `http://localhost:8000/pets/123` — GET single pet
- `http://localhost:8000/docs` — Swagger UI (auto-generated from spec)

## Supported Features

**Data Types:**
- string, integer, number, boolean, array, object
- Nested objects with `$ref` resolution (up to 3 levels deep)
- Circular references handled (return None at depth 4+)

**String Formats:**
- `format: email` → realistic email
- `format: uuid` → valid UUID
- `format: date-time` → ISO 8601 datetime
- `format: date` → YYYY-MM-DD date

**Constraints:**
- `minimum`/`maximum` for integers/numbers
- `minLength`/`maxLength` for strings (respects maxLength with trailing space trim)
- `minItems`/`maxItems` for arrays
- `enum` — picks random value

**Realistic Field Names:**
Field name matching (exact, case-insensitive) generates realistic data via Faker:
- `name`, `first_name`, `last_name` → person names
- `city` → city name
- `street`, `address_line` → street address
- `zipcode`, `postcode`, `zip` → postal code
- `phone` → phone number
- `country` → country name
- `company` → company name
- `description`, `title` → short sentences

Unknown field names generate random lowercase strings.

**Priority:**
1. `format` (email, uuid, date-time, date)
2. `enum` values
3. Field name matching
4. Random generation

**Reproducibility:**
```bash
--seed 42  # Same seed = identical data across requests
```

## Path Parameters

Routes with path parameters include them in response:
```bash
GET /pets/99  # Response includes "id": 99
```

## Error Handling

- Missing route → 404 with `{"error": "Route not found: /path"}`
- Invalid spec → clear error message, exit code 1
- Missing file → clear error message, exit code 1

## Tests

```bash
# Run all tests
.venv\Scripts\python -m pytest -q

# Run specific test
.venv\Scripts\python -m pytest -q tests/test_data_generator.py::TestDataGeneratorFieldNames
```

Coverage: 88 tests
- Spec loading & validation (13)
- Schema resolution with $ref (10)
- Data generation with constraints (31)
- Regression tests (5)
- Field-name data generation (13)
- App integration (8)
- CLI & error handling (7)

## Example Specification

Пример спецификации: `tests/fixtures/petstore.yaml`

## Limitations (MVP)

- ❌ Swagger 2.0 (OpenAPI 3 only)
- ❌ Request body validation
- ❌ Authentication/authorization
- ❌ Custom response codes (uses first 2xx)
- ❌ Example values (generates new random each time)
- ❌ Headers, cookies, security schemes
- ❌ Request/response transformations

## Architecture

- `mockserver/spec_loader.py` — Parse & validate OpenAPI 3 specs
- `mockserver/schema_resolver.py` — Resolve `$ref` references
- `mockserver/data_generator.py` — Generate realistic mock data
- `mockserver/route_builder.py` — Build FastAPI routes dynamically
- `mockserver/app.py` — FastAPI app factory
- `mockserver/cli.py` — Command-line interface
- `mockserver/__main__.py` — Entry point for `python -m mockserver`

## Development

TDD workflow:
1. Write failing tests first
2. Implement code to pass tests
3. All commits tested and atomic

Stack: FastAPI, uvicorn, PyYAML, Faker, pytest
