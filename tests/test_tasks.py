"""
Pytest test cases for Flask Task Management API
File: tests/test_tasks.py
"""

import pytest
import json
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models import User, Task


@pytest.fixture
def app():
    """Create and configure a test Flask application instance"""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_user(app):
    """Create and authenticate a test user"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_headers(client, auth_user):
    """Get authentication headers for API requests"""
    response = client.post('/api/auth/login',
                           json={
                               'username': 'testuser',
                               'password': 'testpassword123'
                           }
                           )
    data = json.loads(response.data)
    token = data.get('token', '')
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_task_data():
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

    def test_create_task_success(self, client, auth_headers, sample_task_data):
        """Test successful task creation"""
        response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['task']['title'] == sample_task_data['title']
        assert data['task']['description'] == sample_task_data['description']
        assert data['task']['category'] == sample_task_data['category']
        assert data['task']['status'] == sample_task_data['status']
        assert data['task']['priority'] == sample_task_data['priority']
        assert 'id' in data['task']

    def test_create_task_without_auth(self, client, sample_task_data):
        """Test task creation without authentication"""
        response = client.post(
            '/api/tasks',
            json=sample_task_data
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False

    def test_create_task_missing_title(self, client, auth_headers, sample_task_data):
        """Test task creation with missing title"""
        del sample_task_data['title']
        response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'title' in data['message'].lower()

    def test_create_task_invalid_status(self, client, auth_headers, sample_task_data):
        """Test task creation with invalid status"""
        sample_task_data['status'] = 'InvalidStatus'
        response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_create_task_invalid_priority(self, client, auth_headers, sample_task_data):
        """Test task creation with invalid priority"""
        sample_task_data['priority'] = 'InvalidPriority'
        response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

    def test_create_task_with_minimal_data(self, client, auth_headers):
        """Test task creation with only required fields"""
        minimal_data = {
            'title': 'Minimal Task'
        }
        response = client.post(
            '/api/tasks',
            json=minimal_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['task']['title'] == 'Minimal Task'


# ============================================================================
# RETRIEVE TASKS TESTS
# ============================================================================

class TestRetrieveTasks:
    """Test cases for retrieving tasks"""

    def test_get_all_tasks_empty(self, client, auth_headers):
        """Test retrieving tasks when none exist"""
        response = client.get('/api/tasks', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tasks']) == 0
        assert data['total'] == 0

    def test_get_all_tasks_success(self, client, auth_headers, sample_task_data, app):
        """Test retrieving all tasks"""
        # Create multiple tasks
        for i in range(3):
            task_data = sample_task_data.copy()
            task_data['title'] = f'Task {i + 1}'
            client.post('/api/tasks', json=task_data, headers=auth_headers)

        response = client.get('/api/tasks', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tasks']) == 3
        assert data['total'] == 3

    def test_get_tasks_without_auth(self, client):
        """Test retrieving tasks without authentication"""
        response = client.get('/api/tasks')

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False

    def test_get_task_by_id_success(self, client, auth_headers, sample_task_data):
        """Test retrieving a specific task by ID"""
        # Create a task
        create_response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = json.loads(create_response.data)['task']['id']

        # Retrieve the task
        response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['task']['id'] == task_id
        assert data['task']['title'] == sample_task_data['title']

    def test_get_task_by_id_not_found(self, client, auth_headers):
        """Test retrieving a non-existent task"""
        response = client.get('/api/tasks/9999', headers=auth_headers)

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False

    def test_filter_tasks_by_status(self, client, auth_headers, sample_task_data):
        """Test filtering tasks by status"""
        # Create tasks with different statuses
        for status in ['Pending', 'In Progress', 'Completed']:
            task_data = sample_task_data.copy()
            task_data['status'] = status
            task_data['title'] = f'Task - {status}'
            client.post('/api/tasks', json=task_data, headers=auth_headers)

        response = client.get('/api/tasks?status=Pending', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert all(task['status'] == 'Pending' for task in data['tasks'])

    def test_filter_tasks_by_category(self, client, auth_headers, sample_task_data):
        """Test filtering tasks by category"""
        # Create tasks with different categories
        for category in ['Work', 'Personal']:
            task_data = sample_task_data.copy()
            task_data['category'] = category
            task_data['title'] = f'Task - {category}'
            client.post('/api/tasks', json=task_data, headers=auth_headers)

        response = client.get('/api/tasks?category=Work', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert all(task['category'] == 'Work' for task in data['tasks'])

    def test_search_tasks(self, client, auth_headers, sample_task_data):
        """Test searching tasks by title or description"""
        task_data = sample_task_data.copy()
        task_data['title'] = 'Unique Search Term'
        client.post('/api/tasks', json=task_data, headers=auth_headers)

        response = client.get('/api/tasks?search=Unique', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tasks']) >= 1
        assert 'Unique' in data['tasks'][0]['title']


# ============================================================================
# UPDATE TASK TESTS
# ============================================================================

class TestUpdateTask:
    """Test cases for updating tasks"""

    def test_update_task_success(self, client, auth_headers, sample_task_data):
        """Test successful task update"""
        # Create a task
        create_response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = json.loads(create_response.data)['task']['id']

        # Update the task
        update_data = {
            'title': 'Updated Task Title',
            'status': 'In Progress',
            'priority': 'Low'
        }
        response = client.put(
            f'/api/tasks/{task_id}',
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['task']['title'] == 'Updated Task Title'
        assert data['task']['status'] == 'In Progress'
        assert data['task']['priority'] == 'Low'

    def test_update_task_without_auth(self, client, sample_task_data):
        """Test updating task without authentication"""
        response = client.put(
            '/api/tasks/1',
            json={'title': 'Updated Title'}
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False

    def test_update_task_not_found(self, client, auth_headers):
        """Test updating a non-existent task"""
        response = client.put(
            '/api/tasks/9999',
            json={'title': 'Updated Title'},
            headers=auth_headers
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False

    def test_update_task_partial(self, client, auth_headers, sample_task_data):
        """Test partial task update (only some fields)"""
        # Create a task
        create_response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = json.loads(create_response.data)['task']['id']
        original_description = sample_task_data['description']

        # Update only the status
        update_data = {'status': 'Completed'}
        response = client.put(
            f'/api/tasks/{task_id}',
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['task']['status'] == 'Completed'
        # Other fields should remain unchanged
        assert data['task']['description'] == original_description

    def test_update_task_mark_complete(self, client, auth_headers, sample_task_data):
        """Test marking a task as complete"""
        # Create a task
        create_response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = json.loads(create_response.data)['task']['id']

        # Mark as complete
        response = client.patch(
            f'/api/tasks/{task_id}/complete',
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['task']['status'] == 'Completed'

    def test_update_task_invalid_data(self, client, auth_headers, sample_task_data):
        """Test updating task with invalid data"""
        # Create a task
        create_response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = json.loads(create_response.data)['task']['id']

        # Try to update with invalid status
        update_data = {'status': 'InvalidStatus'}
        response = client.put(
            f'/api/tasks/{task_id}',
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


# ============================================================================
# DELETE TASK TESTS
# ============================================================================

class TestDeleteTask:
    """Test cases for deleting tasks"""

    def test_delete_task_success(self, client, auth_headers, sample_task_data):
        """Test successful task deletion"""
        # Create a task
        create_response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )
        task_id = json.loads(create_response.data)['task']['id']

        # Delete the task
        response = client.delete(
            f'/api/tasks/{task_id}',
            headers=auth_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == 'Task deleted successfully'

        # Verify task is deleted
        get_response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_task_without_auth(self, client):
        """Test deleting task without authentication"""
        response = client.delete('/api/tasks/1')

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False

    def test_delete_task_not_found(self, client, auth_headers):
        """Test deleting a non-existent task"""
        response = client.delete('/api/tasks/9999', headers=auth_headers)

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False

    def test_delete_task_unauthorized_user(self, client, app, sample_task_data):
        """Test deleting a task by unauthorized user"""
        # Create first user and task
        with app.app_context():
            user1 = User(username='user1', email='user1@example.com')
            user1.set_password('password123')
            db.session.add(user1)
            db.session.commit()

        # Login as user1 and create task
        login_response = client.post('/api/auth/login',
                                     json={'username': 'user1', 'password': 'password123'}
                                     )
        token1 = json.loads(login_response.data)['token']
        headers1 = {'Authorization': f'Bearer {token1}'}

        create_response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=headers1
        )
        task_id = json.loads(create_response.data)['task']['id']

        # Create second user
        with app.app_context():
            user2 = User(username='user2', email='user2@example.com')
            user2.set_password('password123')
            db.session.add(user2)
            db.session.commit()

        # Login as user2
        login_response2 = client.post('/api/auth/login',
                                      json={'username': 'user2', 'password': 'password123'}
                                      )
        token2 = json.loads(login_response2.data)['token']
        headers2 = {'Authorization': f'Bearer {token2}'}

        # Try to delete user1's task as user2
        response = client.delete(f'/api/tasks/{task_id}', headers=headers2)

        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['success'] is False

    def test_delete_multiple_tasks(self, client, auth_headers, sample_task_data):
        """Test deleting multiple tasks"""
        # Create multiple tasks
        task_ids = []
        for i in range(3):
            task_data = sample_task_data.copy()
            task_data['title'] = f'Task {i + 1}'
            response = client.post('/api/tasks', json=task_data, headers=auth_headers)
            task_ids.append(json.loads(response.data)['task']['id'])

        # Delete all tasks
        for task_id in task_ids:
            response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
            assert response.status_code == 200

        # Verify all deleted
        get_response = client.get('/api/tasks', headers=auth_headers)
        data = json.loads(get_response.data)
        assert data['total'] == 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestTaskIntegration:
    """Integration tests for complete task workflows"""

    def test_full_task_lifecycle(self, client, auth_headers, sample_task_data):
        """Test complete task lifecycle: create, read, update, delete"""
        # 1. Create task
        create_response = client.post(
            '/api/tasks',
            json=sample_task_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        task_id = json.loads(create_response.data)['task']['id']

        # 2. Read task
        read_response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
        assert read_response.status_code == 200

        # 3. Update task
        update_response = client.put(
            f'/api/tasks/{task_id}',
            json={'status': 'In Progress'},
            headers=auth_headers
        )
        assert update_response.status_code == 200

        # 4. Delete task
        delete_response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
        assert delete_response.status_code == 200

        # 5. Verify deletion
        final_response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
        assert final_response.status_code == 404

    def test_overdue_task_detection(self, client, auth_headers, sample_task_data):
        """Test detection of overdue tasks"""
        # Create an overdue task
        overdue_data = sample_task_data.copy()
        overdue_data['due_date'] = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        overdue_data['status'] = 'Pending'

        client.post('/api/tasks', json=overdue_data, headers=auth_headers)

        # Get overdue tasks
        response = client.get('/api/tasks?overdue=true', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tasks']) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])