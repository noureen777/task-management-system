"""
Pytest test cases for Flask Task Management API
File: tests/test_tasks.py

Tests the JSON API endpoints with session-based authentication
"""

import pytest
import json
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Task, Category


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

@pytest.fixture
def app():
    """Create and configure a test Flask application instance"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
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
def auth_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    return user_id


@pytest.fixture
def authenticated_client(client, auth_user):
    """Create an authenticated client session"""
    # Login via API
    response = client.post('/api/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'testpassword123'
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    return client


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        'title': 'Test Task',
        'description': 'This is a test task description',
        'status': 'pending',
        'priority': 'high',
        'due_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    }


@pytest.fixture
def sample_category(app, auth_user):
    """Create a sample category"""
    with app.app_context():
        category = Category(
            name='Work',
            color='#0d6efd',
            user_id=auth_user
        )
        db.session.add(category)
        db.session.commit()
        category_id = category.id
    return category_id


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test authentication endpoints"""

    def test_register_success(self, client, app):
        """Test successful user registration"""
        response = client.post('/api/register',
            data=json.dumps({
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Registration successful'
        assert data['username'] == 'newuser'

        # Verify user in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'

    def test_register_duplicate_username(self, client, auth_user):
        """Test registration with duplicate username"""
        response = client.post('/api/register',
            data=json.dumps({
                'username': 'testuser',
                'email': 'different@example.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error'].lower()

    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post('/api/register',
            data=json.dumps({
                'username': 'incomplete'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['error'].lower()

    def test_login_success(self, client, auth_user):
        """Test successful login"""
        response = client.post('/api/login',
            data=json.dumps({
                'username': 'testuser',
                'password': 'testpassword123'
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Login successful'
        assert data['username'] == 'testuser'

    def test_login_invalid_credentials(self, client, auth_user):
        """Test login with invalid credentials"""
        response = client.post('/api/login',
            data=json.dumps({
                'username': 'testuser',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'invalid' in data['error'].lower()

    def test_logout(self, authenticated_client):
        """Test logout"""
        response = authenticated_client.post('/api/logout')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Logout successful'


# ============================================================================
# CREATE TASK TESTS
# ============================================================================

class TestCreateTask:
    """Test cases for creating tasks"""

    def test_create_task_success(self, authenticated_client, sample_task_data, app):
        """Test successful task creation"""
        response = authenticated_client.post('/api/tasks',
            data=json.dumps(sample_task_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == sample_task_data['title']
        assert data['description'] == sample_task_data['description']
        assert data['status'] == sample_task_data['status']
        assert data['priority'] == sample_task_data['priority']
        assert 'id' in data

        # Verify in database
        with app.app_context():
            task = Task.query.filter_by(title='Test Task').first()
            assert task is not None

    def test_create_task_without_auth(self, client, sample_task_data):
        """Test task creation without authentication"""
        response = client.post('/api/tasks',
            data=json.dumps(sample_task_data),
            content_type='application/json'
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_task_missing_title(self, authenticated_client):
        """Test task creation with missing title"""
        response = authenticated_client.post('/api/tasks',
            data=json.dumps({
                'description': 'Task without title'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'title' in data['error'].lower()

    def test_create_task_with_category(self, authenticated_client, sample_category):
        """Test task creation with category"""
        task_data = {
            'title': 'Task with Category',
            'description': 'This task has a category',
            'status': 'pending',
            'priority': 'medium',
            'category_id': sample_category
        }

        response = authenticated_client.post('/api/tasks',
            data=json.dumps(task_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['category_id'] == sample_category

    def test_create_task_minimal_data(self, authenticated_client, app):
        """Test task creation with only required fields"""
        response = authenticated_client.post('/api/tasks',
            data=json.dumps({'title': 'Minimal Task'}),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Minimal Task'
        assert data['status'] == 'pending'  # Default status
        assert data['priority'] == 'medium'  # Default priority


# ============================================================================
# RETRIEVE TASKS TESTS
# ============================================================================

class TestRetrieveTasks:
    """Test cases for retrieving tasks"""

    def test_get_all_tasks_empty(self, authenticated_client):
        """Test retrieving tasks when none exist"""
        response = authenticated_client.get('/api/tasks')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_tasks(self, authenticated_client, sample_task_data, app):
        """Test retrieving all tasks"""
        # Create multiple tasks
        for i in range(3):
            task_data = sample_task_data.copy()
            task_data['title'] = f'Task {i+1}'
            authenticated_client.post('/api/tasks',
                data=json.dumps(task_data),
                content_type='application/json'
            )

        response = authenticated_client.get('/api/tasks')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 3

    def test_get_tasks_without_auth(self, client):
        """Test retrieving tasks without authentication"""
        response = client.get('/api/tasks')

        assert response.status_code == 401

    def test_get_task_by_id(self, authenticated_client, sample_task_data):
        """Test retrieving a specific task by ID"""
        # Create a task
        create_response = authenticated_client.post('/api/tasks',
            data=json.dumps(sample_task_data),
            content_type='application/json'
        )
        task_id = json.loads(create_response.data)['id']

        # Get the task
        response = authenticated_client.get(f'/api/tasks/{task_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == task_id
        assert data['title'] == sample_task_data['title']

    def test_get_nonexistent_task(self, authenticated_client):
        """Test retrieving a non-existent task"""
        response = authenticated_client.get('/api/tasks/9999')

        assert response.status_code == 404

    def test_filter_tasks_by_status(self, authenticated_client, sample_task_data):
        """Test filtering tasks by status"""
        # Create tasks with different statuses
        for status in ['pending', 'in-progress', 'completed']:
            task_data = sample_task_data.copy()
            task_data['status'] = status
            task_data['title'] = f'Task - {status}'
            authenticated_client.post('/api/tasks',
                data=json.dumps(task_data),
                content_type='application/json'
            )

        response = authenticated_client.get('/api/tasks?status=pending')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(task['status'] == 'pending' for task in data)

    def test_filter_tasks_by_priority(self, authenticated_client, sample_task_data):
        """Test filtering tasks by priority"""
        # Create tasks with different priorities
        for priority in ['low', 'medium', 'high']:
            task_data = sample_task_data.copy()
            task_data['priority'] = priority
            task_data['title'] = f'Task - {priority}'
            authenticated_client.post('/api/tasks',
                data=json.dumps(task_data),
                content_type='application/json'
            )

        response = authenticated_client.get('/api/tasks?priority=high')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(task['priority'] == 'high' for task in data)

    def test_search_tasks(self, authenticated_client, sample_task_data):
        """Test searching tasks"""
        task_data = sample_task_data.copy()
        task_data['title'] = 'Unique Search Term Task'
        authenticated_client.post('/api/tasks',
            data=json.dumps(task_data),
            content_type='application/json'
        )

        response = authenticated_client.get('/api/tasks?search=Unique')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert 'Unique' in data[0]['title']


# ============================================================================
# UPDATE TASK TESTS
# ============================================================================

class TestUpdateTask:
    """Test cases for updating tasks"""

    def test_update_task_success(self, authenticated_client, sample_task_data, app):
        """Test successful task update"""
        # Create a task
        create_response = authenticated_client.post('/api/tasks',
            data=json.dumps(sample_task_data),
            content_type='application/json'
        )
        task_id = json.loads(create_response.data)['id']

        # Update the task
        update_data = {
            'title': 'Updated Task Title',
            'status': 'completed',
            'priority': 'low'
        }
        response = authenticated_client.put(f'/api/tasks/{task_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated Task Title'
        assert data['status'] == 'completed'
        assert data['priority'] == 'low'

        # Verify in database
        with app.app_context():
            task = Task.query.get(task_id)
            assert task.title == 'Updated Task Title'

    def test_update_task_without_auth(self, client):
        """Test updating task without authentication"""
        response = client.put('/api/tasks/1',
            data=json.dumps({'title': 'Updated'}),
            content_type='application/json'
        )

        assert response.status_code == 401

    def test_update_nonexistent_task(self, authenticated_client):
        """Test updating a non-existent task"""
        response = authenticated_client.put('/api/tasks/9999',
            data=json.dumps({'title': 'Updated'}),
            content_type='application/json'
        )

        assert response.status_code == 404

    def test_update_task_partial(self, authenticated_client, sample_task_data):
        """Test partial task update"""
        # Create a task
        create_response = authenticated_client.post('/api/tasks',
            data=json.dumps(sample_task_data),
            content_type='application/json'
        )
        task_id = json.loads(create_response.data)['id']
        original_description = sample_task_data['description']

        # Update only the status
        response = authenticated_client.put(f'/api/tasks/{task_id}',
            data=json.dumps({'status': 'completed'}),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'completed'
        assert data['description'] == original_description


# ============================================================================
# DELETE TASK TESTS
# ============================================================================

class TestDeleteTask:
    """Test cases for deleting tasks"""

    def test_delete_task_success(self, authenticated_client, sample_task_data, app):
        """Test successful task deletion"""
        # Create a task
        create_response = authenticated_client.post('/api/tasks',
            data=json.dumps(sample_task_data),
            content_type='application/json'
        )
        task_id = json.loads(create_response.data)['id']

        # Delete the task
        response = authenticated_client.delete(f'/api/tasks/{task_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Task deleted successfully'

        # Verify deletion
        with app.app_context():
            task = Task.query.get(task_id)
            assert task is None

    def test_delete_task_without_auth(self, client):
        """Test deleting task without authentication"""
        response = client.delete('/api/tasks/1')

        assert response.status_code == 401

    def test_delete_nonexistent_task(self, authenticated_client):
        """Test deleting a non-existent task"""
        response = authenticated_client.delete('/api/tasks/9999')

        assert response.status_code == 404

    def test_delete_other_users_task(self, client, app, sample_task_data):
        """Test that users cannot delete other users' tasks"""
        # Create first user and task
        with app.app_context():
            user1 = User(username='user1', email='user1@test.com')
            user1.set_password('password123')
            db.session.add(user1)
            db.session.commit()

        # Login as user1 and create task
        client.post('/api/login',
            data=json.dumps({
                'username': 'user1',
                'password': 'password123'
            }),
            content_type='application/json'
        )

        create_response = client.post('/api/tasks',
            data=json.dumps(sample_task_data),
            content_type='application/json'
        )
        task_id = json.loads(create_response.data)['id']

        # Logout
        client.post('/api/logout')

        # Create and login as user2
        with app.app_context():
            user2 = User(username='user2', email='user2@test.com')
            user2.set_password('password123')
            db.session.add(user2)
            db.session.commit()

        client.post('/api/login',
            data=json.dumps({
                'username': 'user2',
                'password': 'password123'
            }),
            content_type='application/json'
        )

        # Try to delete user1's task
        response = client.delete(f'/api/tasks/{task_id}')

        # Should return 404 (not found for this user)
        assert response.status_code == 404


# ============================================================================
# DASHBOARD STATS TESTS
# ============================================================================

class TestDashboardStats:
    """Test cases for dashboard statistics"""

    def test_get_stats_empty(self, authenticated_client):
        """Test getting stats when no tasks exist"""
        response = authenticated_client.get('/api/stats')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_tasks'] == 0
        assert data['completed'] == 0
        assert data['pending'] == 0
        assert data['completion_rate'] == 0

    def test_get_stats_with_tasks(self, authenticated_client, sample_task_data):
        """Test getting stats with tasks"""
        # Create tasks with different statuses
        statuses = ['pending', 'in-progress', 'completed', 'completed']
        for i, status in enumerate(statuses):
            task_data = sample_task_data.copy()
            task_data['status'] = status
            task_data['title'] = f'Task {i+1}'
            authenticated_client.post('/api/tasks',
                data=json.dumps(task_data),
                content_type='application/json'
            )

        response = authenticated_client.get('/api/stats')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_tasks'] == 4
        assert data['completed'] == 2
        assert data['pending'] == 1
        assert data['in_progress'] == 1
        assert data['completion_rate'] == 50.0

    def test_stats_without_auth(self, client):
        """Test getting stats without authentication"""
        response = client.get('/api/stats')

        assert response.status_code == 401


# ============================================================================
# CATEGORY TESTS
# ============================================================================

class TestCategories:
    """Test cases for category management"""

    def test_get_categories(self, authenticated_client, app, auth_user):
        """Test retrieving categories"""
        response = authenticated_client.get('/api/categories')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        # Should have default categories from registration
        assert len(data) >= 4

    def test_create_category(self, authenticated_client, app):
        """Test creating a custom category"""
        category_data = {
            'name': 'Custom Category',
            'color': '#ff5733'
        }

        response = authenticated_client.post('/api/categories',
            data=json.dumps(category_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Custom Category'
        assert data['color'] == '#ff5733'

    def test_delete_category(self, authenticated_client, sample_category):
        """Test deleting a category"""
        response = authenticated_client.delete(f'/api/categories/{sample_category}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Category deleted successfully'


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_complete_task_lifecycle(self, authenticated_client, sample_task_data, app):
        """Test complete CRUD workflow"""
        # 1. Create task
        create_response = authenticated_client.post('/api/tasks',
            data=json.dumps(sample_task_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        task_id = json.loads(create_response.data)['id']

        # 2. Read task
        read_response = authenticated_client.get(f'/api/tasks/{task_id}')
        assert read_response.status_code == 200

        # 3. Update task
        update_response = authenticated_client.put(f'/api/tasks/{task_id}',
            data=json.dumps({'status': 'completed'}),
            content_type='application/json'
        )
        assert update_response.status_code == 200

        # 4. Delete task
        delete_response = authenticated_client.delete(f'/api/tasks/{task_id}')
        assert delete_response.status_code == 200

        # 5. Verify deletion
        final_response = authenticated_client.get(f'/api/tasks/{task_id}')
        assert final_response.status_code == 404

    def test_user_isolation(self, client, app, sample_task_data):
        """Test that users can only see their own tasks"""
        # Create two users
        with app.app_context():
            user1 = User(username='user1', email='user1@test.com')
            user1.set_password('pass123')
            user2 = User(username='user2', email='user2@test.com')
            user2.set_password('pass123')
            db.session.add_all([user1, user2])
            db.session.commit()

        # User1 creates tasks
        client.post('/api/login',
            data=json.dumps({'username': 'user1', 'password': 'pass123'}),
            content_type='application/json'
        )
        client.post('/api/tasks',
            data=json.dumps(sample_task_data),
            content_type='application/json'
        )
        client.post('/api/logout')

        # User2 logs in and checks tasks
        client.post('/api/login',
            data=json.dumps({'username': 'user2', 'password': 'pass123'}),
            content_type='application/json'
        )
        response = client.get('/api/tasks')
        data = json.loads(response.data)

        # User2 should see 0 tasks
        assert len(data) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])