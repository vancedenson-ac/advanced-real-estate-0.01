"""Tests for task status endpoints."""
import pytest
from fastapi import status
from unittest.mock import Mock, patch
from celery.result import AsyncResult


def test_get_task_status_pending(client):
    """Test get task status for pending task."""
    with patch('app.routes.tasks.AsyncResult') as mock_async_result:
        mock_result = Mock()
        mock_result.state = 'PENDING'
        mock_result.info = None
        mock_async_result.return_value = mock_result
        
        response = client.get("/api/tasks/test-task-id")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "pending"
        assert data["result"] is None
        assert data["error"] is None


def test_get_task_status_success(client):
    """Test get task status for successful task."""
    with patch('app.routes.tasks.AsyncResult') as mock_async_result:
        mock_result = Mock()
        mock_result.state = 'SUCCESS'
        mock_result.result = {
            "status": "success",
            "image_id": 123,
            "predictions": {"room_type": {"label": "kitchen"}}
        }
        mock_async_result.return_value = mock_result
        
        response = client.get("/api/tasks/test-task-id")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["result"] is not None
        assert "image_id" in data["result"]


def test_get_task_status_failure(client):
    """Test get task status for failed task."""
    with patch('app.routes.tasks.AsyncResult') as mock_async_result:
        mock_result = Mock()
        mock_result.state = 'FAILURE'
        mock_result.info = "Task failed with error"
        mock_async_result.return_value = mock_result
        
        response = client.get("/api/tasks/test-task-id")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "failure"
        assert data["error"] is not None


def test_get_task_status_progress(client):
    """Test get task status for in-progress task."""
    with patch('app.routes.tasks.AsyncResult') as mock_async_result:
        mock_result = Mock()
        mock_result.state = 'PROGRESS'
        mock_result.info = {"current": 50, "total": 100}
        mock_async_result.return_value = mock_result
        
        response = client.get("/api/tasks/test-task-id")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["result"] is not None

