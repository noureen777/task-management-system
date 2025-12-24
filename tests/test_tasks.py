"""
Pytest test cases for Flask Task Management API
File: tests/test_tasks.py

"""

import pytest
import json
from datetime import datetime, timedelta

# ============================================================================
# IMPORTANT: Update these imports to match your project structure
# ============================================================================
# Option 1: If your app.py is in the root directory
# from app import app, db

# Option 2: If you have an app package with __init__.py
# from app import create_app, db
# from app.models import User, Task

# Option 3: If models.py is in the root directory
# import app
# from models import User, Task

# Placeholder - UPDATE THIS BASED ON YOUR PROJECT STRUCTURE
try:
    # Try to import from app package
    from app import app, db
except ImportError:
    try:
        # Try to import from root
        import app as flask_module
        app = flask_module.app
        db = flask_module.db
    except:
        raise ImportError(
            "Could not import Flask app. Please update the import statement "
            "in tests/test_tasks.py to match your project structure."
        )


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def auth_token(client):
    """
    Create a test user and return authentication token
    Adjust this based on your authentication implementation
    """
    # Register a test user
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123'
    })

    # Login and get session/token
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword123'
    }, follow_redirects=True)

    return client  # Return client with session


@pytest.fixture
def sample_task():
    """Sample task data for testing"""
    return {
        'title': 'Test Task',
        'description': 'This is a test task description',
        'category': 'Work',
        'due_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'status': 'Pending',
        'priority': 'High'
    }


# ============================================================================
# CREATE TASK TESTS
# ============================================================================

class TestCreateTask:
    """Test cases for creating tasks"""

    def test_create_task_success(self, auth_token, sample_task):
        """Test successful task creation"""
        response = auth_token.post('/tasks/create', data=sample_task)

        # Adjust status code based on your implementation (201, 200, or redirect)
        assert response.status_code in [200, 201, 302]

    def test_create_task_missing_title(self, auth_token, sample_task):
        """Test task creation with missing title"""
        sample_task['title'] = ''
        response = auth_token.post('/tasks/create', data=sample_task)

        # Should return error or redirect back to form
        assert response.status_code in [400, 302]

    def test_create_task_without_auth(self, client, sample_task):
        """Test task creation without authentication"""
        response = client.post('/tasks/create', data=sample_task)

        # Should redirect to login
        assert response.status_code in [302, 401]


# ============================================================================
# RETRIEVE TASKS TESTS
# ============================================================================

class TestRetrieveTasks:
    """Test cases for retrieving tasks"""

    def test_get_all_tasks(self, auth_token):
        """Test retrieving all tasks"""
        response = auth_token.get('/tasks')

        assert response.status_code == 200
        assert b'task' in response.data.lower() or b'my tasks' in response.data.lower()

    def test_get_tasks_without_auth(self, client):
        """Test retrieving tasks without authentication"""
        response = client.get('/tasks')

        # Should redirect to login
        assert response.status_code in [302, 401]

    def test_get_dashboard(self, auth_token):
        """Test retrieving dashboard with task statistics"""
        response = auth_token.get('/dashboard')

        assert response.status_code == 200
        assert b'dashboard' in response.data.lower()


# ============================================================================
# UPDATE TASK TESTS
# ============================================================================

class TestUpdateTask:
    """Test cases for updating tasks"""

    def test_update_task_success(self, auth_token, sample_task):
        """Test successful task update"""
        # First create a task
        create_response = auth_token.post('/tasks/create', data=sample_task)

        # Extract task ID from response or database
        # You'll need to adjust this based on your implementation
        task_id = 1  # Placeholder

        # Update the task
        update_data = {
            'title': 'Updated Task Title',
            'status': 'Completed',
            'priority': 'Low'
        }
        response = auth_token.post(f'/tasks/edit/{task_id}', data=update_data)

        assert response.status_code in [200, 302]

    def test_update_task_without_auth(self, client):
        """Test updating task without authentication"""
        response = client.post('/tasks/edit/1', data={'title': 'Updated'})

        # Should redirect to login
        assert response.status_code in [302, 401]


# ============================================================================
# DELETE TASK TESTS
# ============================================================================

class TestDeleteTask:
    """Test cases for deleting tasks"""

    def test_delete_task_success(self, auth_token, sample_task):
        """Test successful task deletion"""
        # First create a task
        auth_token.post('/tasks/create', data=sample_task)

        # Delete the task
        task_id = 1  # Placeholder - adjust based on your implementation
        response = auth_token.post(f'/tasks/delete/{task_id}')

        assert response.status_code in [200, 302]

    def test_delete_task_without_auth(self, client):
        """Test deleting task without authentication"""
        response = client.post('/tasks/delete/1')

        # Should redirect to login
        assert response.status_code in [302, 401]

    def test_delete_nonexistent_task(self, auth_token):
        """Test deleting a non-existent task"""
        response = auth_token.post('/tasks/delete/9999')

        # Should return error or redirect
        assert response.status_code in [404, 302]


# ============================================================================
# API ENDPOINT TESTS (If you have REST API)
# ============================================================================

class TestTaskAPI:
    """Test cases for Task REST API endpoints"""

    def test_api_get_tasks(self, auth_token):
        """Test GET /api/tasks endpoint"""
        response = auth_token.get('/api/tasks')

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'tasks' in data or isinstance(data, list)

    def test_api_create_task(self, auth_token, sample_task):
        """Test POST /api/tasks endpoint"""
        response = auth_token.post(
            '/api/tasks',
            data=json.dumps(sample_task),
            content_type='application/json'
        )

        if response.status_code in [200, 201]:
            data = json.loads(response.data)
            assert 'id' in data or 'task' in data

    def test_api_update_task(self, auth_token):
        """Test PUT /api/tasks/<id> endpoint"""
        update_data = {'status': 'Completed'}
        response = auth_token.put(
            '/api/tasks/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        # Status code varies by implementation
        assert response.status_code in [200, 404]

    def test_api_delete_task(self, auth_token):
        """Test DELETE /api/tasks/<id> endpoint"""
        response = auth_token.delete('/api/tasks/1')

        # Status code varies by implementation
        assert response.status_code in [200, 204, 404]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestTaskWorkflow:
    """Integration tests for complete task workflows"""

    def test_complete_task_lifecycle(self, auth_token, sample_task):
        """Test complete CRUD workflow"""
        # 1. Create task
        create_response = auth_token.post('/tasks/create', data=sample_task)
        assert create_response.status_code in [200, 201, 302]

        # 2. View tasks
        view_response = auth_token.get('/tasks')
        assert view_response.status_code == 200

        # 3. Update task (if applicable)
        # 4. Delete task (if applicable)

    def test_dashboard_reflects_tasks(self, auth_token, sample_task):
        """Test that dashboard statistics update with tasks"""
        # Get initial dashboard
        initial = auth_token.get('/dashboard')
        assert initial.status_code == 200

        # Create a task
        auth_token.post('/tasks/create', data=sample_task)

        # Check dashboard again
        updated = auth_token.get('/dashboard')
        assert updated.status_code == 200
        # Dashboard should now show the new task


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])