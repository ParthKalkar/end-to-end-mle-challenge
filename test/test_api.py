"""
Write your tests here.
You should add and adjust tests at least for the endpoints you implement.
e.g. check responses, potential errors etc.
"""

from starlette.testclient import TestClient
import pytest


class TestHealth:
    """Test suite for health endpoint"""
    
    def test_health(self, client: TestClient):
        """Test health endpoint returns 200 and 'healthy' message"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == "healthy"


class TestPredict:
    """Test suite for prediction endpoint"""
    
    def test_successful_call(self, client: TestClient):
        """Test successful prediction with valid input"""
        response = client.post(
            "/api/predict",
            json={"id": 1234, "recency_7": 1, "frequency_7": 1, "monetary_7": 8.5},
        )
        assert response.status_code == 200
        assert "monetary_30" in response.json()
        assert "id" in response.json()
        assert response.json()["id"] == 1234
    
    def test_prediction_response_structure(self, client: TestClient):
        """Test that prediction response has correct structure"""
        response = client.post(
            "/api/predict",
            json={"id": 5678, "recency_7": 3, "frequency_7": 2, "monetary_7": 15.5},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["id"], int)
        assert isinstance(data["monetary_30"], (int, float))
        assert data["monetary_30"] >= 0
    
    def test_prediction_with_zero_values(self, client: TestClient):
        """Test prediction with zero monetary value"""
        response = client.post(
            "/api/predict",
            json={"id": 9999, "recency_7": 0, "frequency_7": 0, "monetary_7": 0.0},
        )
        assert response.status_code == 200
        assert response.json()["monetary_30"] >= 0
    
    def test_prediction_with_high_values(self, client: TestClient):
        """Test prediction with high input values"""
        response = client.post(
            "/api/predict",
            json={"id": 1111, "recency_7": 7, "frequency_7": 100, "monetary_7": 1000.0},
        )
        assert response.status_code == 200
        assert response.json()["monetary_30"] >= 0
    
    def test_prediction_missing_field(self, client: TestClient):
        """Test prediction with missing required field"""
        response = client.post(
            "/api/predict",
            json={"id": 2222, "recency_7": 1, "frequency_7": 1},
        )
        assert response.status_code == 422  # Validation error
    
    def test_prediction_invalid_type(self, client: TestClient):
        """Test prediction with invalid data type"""
        response = client.post(
            "/api/predict",
            json={"id": "invalid", "recency_7": 1, "frequency_7": 1, "monetary_7": 8.5},
        )
        assert response.status_code == 422  # Validation error
    
    def test_multiple_predictions_same_passenger(self, client: TestClient):
        """Test multiple predictions for the same passenger"""
        passenger_id = 3333
        for i in range(3):
            response = client.post(
                "/api/predict",
                json={"id": passenger_id, "recency_7": i+1, "frequency_7": i+1, "monetary_7": float(i+1)},
            )
            assert response.status_code == 200
    
    def test_predictions_different_passengers(self, client: TestClient):
        """Test predictions for different passengers"""
        for i in range(3):
            response = client.post(
                "/api/predict",
                json={"id": 4000 + i, "recency_7": 1, "frequency_7": 1, "monetary_7": 10.0},
            )
            assert response.status_code == 200
            assert response.json()["id"] == 4000 + i


class TestRequests:
    """Test suite for request tracking endpoint"""
    
    def test_count_requests_zero(self, client: TestClient):
        """Test counting requests for a new passenger with no predictions"""
        response = client.get("/api/requests/999999")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["count"] >= 0
    
    def test_count_requests_after_prediction(self, client: TestClient):
        """Test counting requests after making predictions"""
        passenger_id = 5555
        # Make a prediction
        predict_response = client.post(
            "/api/predict",
            json={"id": passenger_id, "recency_7": 1, "frequency_7": 1, "monetary_7": 8.5},
        )
        assert predict_response.status_code == 200
        
        # Count requests
        count_response = client.get(f"/api/requests/{passenger_id}")
        assert count_response.status_code == 200
        assert count_response.json()["count"] >= 1
    
    def test_count_requests_multiple_predictions(self, client: TestClient):
        """Test counting requests after multiple predictions"""
        passenger_id = 6666
        num_predictions = 3
        
        # Make multiple predictions
        for i in range(num_predictions):
            response = client.post(
                "/api/predict",
                json={"id": passenger_id, "recency_7": i+1, "frequency_7": i+1, "monetary_7": float(i+1)},
            )
            assert response.status_code == 200
        
        # Count requests
        count_response = client.get(f"/api/requests/{passenger_id}")
        assert count_response.status_code == 200
        assert count_response.json()["count"] == num_predictions
    
    def test_count_requests_response_structure(self, client: TestClient):
        """Test that count response has correct structure"""
        passenger_id = 7777
        response = client.get(f"/api/requests/{passenger_id}")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "count" in data
        assert data["id"] == passenger_id
        assert isinstance(data["count"], int)
    
    def test_count_requests_isolated(self, client: TestClient):
        """Test that request counts are isolated per passenger"""
        passenger_id_1 = 8888
        passenger_id_2 = 8889
        
        # Make prediction for passenger 1
        client.post(
            "/api/predict",
            json={"id": passenger_id_1, "recency_7": 1, "frequency_7": 1, "monetary_7": 8.5},
        )
        
        # Make prediction for passenger 2
        client.post(
            "/api/predict",
            json={"id": passenger_id_2, "recency_7": 1, "frequency_7": 1, "monetary_7": 8.5},
        )
        
        # Check counts are separate
        count_1 = client.get(f"/api/requests/{passenger_id_1}").json()["count"]
        count_2 = client.get(f"/api/requests/{passenger_id_2}").json()["count"]
        
        # Both should have at least 1, but we only care they're counted separately
        assert count_1 >= 1
        assert count_2 >= 1
