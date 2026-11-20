import pytest
from fastapi.testclient import TestClient
from mockserver.app import create_app


class TestApp:
    """Tests for FastAPI app integration"""

    def test_get_pets_returns_array(self, petstore_spec):
        """GET /pets returns array of pets (2-5 items)"""
        app = create_app(petstore_spec, seed=42)
        client = TestClient(app)

        response = client.get("/pets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert 2 <= len(data) <= 5

    def test_get_pets_array_items_have_required_fields(self, petstore_spec):
        """Each pet in GET /pets has id, name, status"""
        app = create_app(petstore_spec, seed=42)
        client = TestClient(app)

        response = client.get("/pets")
        data = response.json()

        for pet in data:
            assert "id" in pet
            assert "name" in pet
            assert "status" in pet
            assert isinstance(pet["id"], int)
            assert isinstance(pet["name"], str)
            assert pet["status"] in ["available", "pending", "sold"]

    def test_get_pet_by_id_returns_object(self, petstore_spec):
        """GET /pets/42 returns single pet object"""
        app = create_app(petstore_spec, seed=42)
        client = TestClient(app)

        response = client.get("/pets/42")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, dict)
        assert "id" in data
        assert "name" in data
        assert "status" in data

    def test_post_pets_returns_201(self, petstore_spec):
        """POST /pets returns 201 Created"""
        app = create_app(petstore_spec, seed=42)
        client = TestClient(app)

        pet_data = {
            "id": 1,
            "name": "Fluffy",
            "status": "available"
        }
        response = client.post("/pets", json=pet_data)
        assert response.status_code == 201
        data = response.json()
        assert isinstance(data, dict)

    def test_unknown_route_returns_404(self, petstore_spec):
        """GET /unknown → 404 with JSON error"""
        app = create_app(petstore_spec, seed=42)
        client = TestClient(app)

        response = client.get("/unknown-route-xyz")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert isinstance(data["error"], str)

    def test_seed_reproducibility_same_app(self, petstore_spec):
        """Same seed produces identical responses"""
        app1 = create_app(petstore_spec, seed=123)
        client1 = TestClient(app1)

        app2 = create_app(petstore_spec, seed=123)
        client2 = TestClient(app2)

        response1 = client1.get("/pets")
        response2 = client2.get("/pets")

        assert response1.json() == response2.json()

    def test_different_seed_different_data(self, petstore_spec):
        """Different seeds produce different data"""
        app1 = create_app(petstore_spec, seed=100)
        client1 = TestClient(app1)

        app2 = create_app(petstore_spec, seed=200)
        client2 = TestClient(app2)

        response1 = client1.get("/pets")
        response2 = client2.get("/pets")

        # Different seeds usually produce different data (very likely)
        assert response1.json() != response2.json()

    def test_path_parameter_in_response(self, petstore_spec):
        """Path parameter /pets/{id} should be included in response"""
        app = create_app(petstore_spec, seed=42)
        client = TestClient(app)

        response = client.get("/pets/99")
        data = response.json()

        # The response should include the id from the path
        assert "id" in data
        # ID should be the parameter value (99)
        assert data["id"] == 99
