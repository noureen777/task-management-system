"""
Pytest test cases for Flask Task Management API
File: tests/test_tasks.py
"""

import pytest
import json
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from your app package
from app import create_app, db
from app.models import User, Task


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
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_user(app):
    """Create a test user and return the user object"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()

        # Return the user id for use in tests
        user_id = user.id

    return user_id


@pytest.fixture
def authenticated_client(client, auth_user):
    """Create an authenticated client session"""
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword123'
    }, follow_redirects=True)

    return client


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

    def test_create_task_success(self, authenticated_client, sample_task_data):
        """Test successful task creation"""
        response = authenticated_client.post(
            '/tasks/create',
            data=sample_task_data,
            follow_redirects=True
        )

        assert response.status_code == 200
        # Check if redirected to tasks page or success message
        assert b'Task' in response.data or b'Success' in response.data

    def test_create_task_without_auth(self, client, sample_task_data):
        """Test task creation without authentication"""
        response = client.post('/tasks/create', data=sample_task_data)

        # Should redirect to login
        assert response.status_code == 302
        assert b'/login' in response.data or response.location and 'login' in response.location

    def test_create_task_missing_title(self, authenticated_client, sample_task_data):
        """Test task creation with missing title"""
        sample_task_data['title'] = ''
        response = authenticated_client.post(
            '/tasks/create',
            data=sample_task_data,
            follow_redirects=True
        )

        # Should show error or stay on form
        assert response.status_code == 200

    def test_create_task_with_minimal_data(self, authenticated_client):
        """Test task creation with only required fields"""
        minimal_data = {
            'title': 'Minimal Task'
        }
        response = authenticated_client.post(
            '/tasks/create',
            data=minimal_data,
            follow_redirects=True
        )

        assert response.status_code == 200


# ============================================================================
# RETRIEVE TASKS TESTS
# ============================================================================

class TestRetrieveTasks:
    """Test cases for retrieving tasks"""

    def test_get_all_tasks_page(self, authenticated_client):
        """Test accessing the tasks page"""
        response = authenticated_client.get('/tasks')

        assert response.status_code == 200
        assert b'Task' in response.data or b'My Tasks' in response.data

    def test_get_tasks_without_auth(self, client):
        """Test retrieving tasks without authentication"""
        response = client.get('/tasks')

        # Should redirect to login
        assert response.status_code == 302

    def test_get_dashboard(self, authenticated_client):
        """Test accessing the dashboard"""
        response = authenticated_client.get('/dashboard')

        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'dashboard' in response.data

    def test_tasks_appear_in_list(self, authenticated_client, sample_task_data):
        """Test that created tasks appear in the task list"""
        # Create a task
        authenticated_client.post('/tasks/create', data=sample_task_data)

        # Get tasks page
        response = authenticated_client.get('/tasks')

        assert response.status_code == 200
        assert sample_task_data['title'].encode() in response.data

    def test_dashboard_shows_statistics(self, authenticated_client, sample_task_data):
        """Test that dashboard shows task statistics"""
        # Create some tasks
        authenticated_client.post('/tasks/create', data=sample_task_data)

        response = authenticated_client.get('/dashboard')

        assert response.status_code == 200
        # Check for common dashboard elements
        assert b'Total' in response.data or b'Completed' in response.data


# ============================================================================
# UPDATE TASK TESTS
# ============================================================================

class TestUpdateTask:
    """Test cases for updating tasks"""

    def test_update_task_success(self, authenticated_client, sample_task_data, app):
        """Test successful task update"""
        # Create a task
        authenticated_client.post('/tasks/create', data=sample_task_data)

        # Get the task ID from database
        with app.app_context():
            task = Task.query.first()
            task_id = task.id

        # Update the task
        update_data = {
            'title': 'Updated Task Title',
            'status': 'Completed',
            'priority': 'Low'
        }
        response = authenticated_client.post(
            f'/tasks/edit/{task_id}',
            data=update_data,
            follow_redirects=True
        )

        assert response.status_code == 200

        # Verify update in database
        with app.app_context():
            updated_task = Task.query.get(task_id)
            assert updated_task.title == 'Updated Task Title'
            assert updated_task.status == 'Completed'

    def test_update_task_without_auth(self, client):
        """Test updating task without authentication"""
        response = client.post('/tasks/edit/1', data={'title': 'Updated'})

        # Should redirect to login
        assert response.status_code == 302

    def test_update_nonexistent_task(self, authenticated_client):
        """Test updating a non-existent task"""
        response = authenticated_client.post(
            '/tasks/edit/9999',
            data={'title': 'Updated'},
            follow_redirects=True
        )

        # Should show error or redirect
        assert response.status_code in [200, 404]


# ============================================================================
# DELETE TASK TESTS
# ============================================================================

class TestDeleteTask:
    """Test cases for deleting tasks"""

    def test_delete_task_success(self, authenticated_client, sample_task_data, app):
        """Test successful task deletion"""
        # Create a task
        authenticated_client.post('/tasks/create', data=sample_task_data)

        # Get the task ID
        with app.app_context():
            task = Task.query.first()
            task_id = task.id

        # Delete the task
        response = authenticated_client.post(
            f'/tasks/delete/{task_id}',
            follow_redirects=True
        )

        assert response.status_code == 200

        # Verify deletion
        with app.app_context():
            deleted_task = Task.query.get(task_id)
            assert deleted_task is None

    def test_delete_task_without_auth(self, client):
        """Test deleting task without authentication"""
        response = client.post('/tasks/delete/1')

        # Should redirect to login
        assert response.status_code == 302

    def test_delete_nonexistent_task(self, authenticated_client):
        """Test deleting a non-existent task"""
        response = authenticated_client.post(
            '/tasks/delete/9999',
            follow_redirects=True
        )

        # Should handle gracefully
        assert response.status_code in [200, 404]

    def test_delete_other_users_task(self, client, app, sample_task_data):
        """Test that users cannot delete other users' tasks"""
        # Create first user and task
        with app.app_context():
            user1 = User(username='user1', email='user1@test.com')
            user1.set_password('password123')
            db.session.add(user1)
            db.session.commit()
            user1_id = user1.id

        # Login as user1 and create task
        client.post('/login', data={
            'username': 'user1',
            'password': 'password123'
        })
        client.post('/tasks/create', data=sample_task_data)

        with app.app_context():
            task = Task.query.filter_by(user_id=user1_id).first()
            task_id = task.id

        # Logout
        client.get('/logout')

        # Create and login as user2
        with app.app_context():
            user2 = User(username='user2', email='user2@test.com')
            user2.set_password('password123')
            db.session.add(user2)
            db.session.commit()

        client.post('/login', data={
            'username': 'user2',
            'password': 'password123'
        })

        # Try to delete user1's task
        response = client.post(f'/tasks/delete/{task_id}', follow_redirects=True)

        # Task should still exist
        with app.app_context():
            task = Task.query.get(task_id)
            assert task is not None


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestTaskWorkflow:
    """Integration tests for complete task workflows"""

    def test_complete_task_lifecycle(self, authenticated_client, sample_task_data, app):
        """Test complete CRUD workflow"""
        # 1. Create task
        create_response = authenticated_client.post(
            '/tasks/create',
            data=sample_task_data,
            follow_redirects=True
        )
        assert create_response.status_code == 200

        # Get task ID
        with app.app_context():
            task = Task.query.first()
            task_id = task.id

        # 2. View tasks
        view_response = authenticated_client.get('/tasks')
        assert view_response.status_code == 200
        assert sample_task_data['title'].encode() in view_response.data

        # 3. Update task
        update_response = authenticated_client.post(
            f'/tasks/edit/{task_id}',
            data={'title': 'Updated Title', 'status': 'Completed'},
            follow_redirects=True
        )
        assert update_response.status_code == 200

        # 4. Delete task
        delete_response = authenticated_client.post(
            f'/tasks/delete/{task_id}',
            follow_redirects=True
        )
        assert delete_response.status_code == 200

        # 5. Verify deletion
        with app.app_context():
            deleted_task = Task.query.get(task_id)
            assert deleted_task is None

    def test_dashboard_updates_with_tasks(self, authenticated_client, sample_task_data):
        """Test that dashboard statistics update when tasks are created"""
        # Get initial dashboard
        initial_response = authenticated_client.get('/dashboard')
        assert initial_response.status_code == 200

        # Create multiple tasks with different statuses
        for status in ['Pending', 'In Progress', 'Completed']:
            task_data = sample_task_data.copy()
            task_data['status'] = status
            task_data['title'] = f'Task - {status}'
            authenticated_client.post('/tasks/create', data=task_data)

        # Check updated dashboard
        updated_response = authenticated_client.get('/dashboard')
        assert updated_response.status_code == 200
        # Dashboard should reflect the new tasks
        assert b'3' in updated_response.data or b'Total' in updated_response.data

    def test_filter_tasks_by_category(self, authenticated_client, sample_task_data, app):
        """Test filtering tasks by category"""
        # Create tasks with different categories
        for category in ['Work', 'Personal']:
            task_data = sample_task_data.copy()
            task_data['category'] = category
            task_data['title'] = f'{category} Task'
            authenticated_client.post('/tasks/create', data=task_data)

        # Filter by Work category
        response = authenticated_client.get('/tasks?category=Work')
        assert response.status_code == 200
        assert b'Work Task' in response.data


# ============================================================================
# DATABASE MODEL TESTS
# ============================================================================

class TestModels:
    """Test database models"""

    def test_user_model(self, app):
        """Test User model creation"""
        with app.app_context():
            user = User(username='modeltest', email='model@test.com')
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()

            # Retrieve and verify
            retrieved_user = User.query.filter_by(username='modeltest').first()
            assert retrieved_user is not None
            assert retrieved_user.email == 'model@test.com'
            assert retrieved_user.check_password('testpass')

    def test_task_model(self, app, auth_user):
        """Test Task model creation"""
        with app.app_context():
            task = Task(
                user_id=auth_user,
                title='Model Test Task',
                description='Testing the task model',
                status='Pending',
                priority='High',
                category='Work'
            )
            db.session.add(task)
            db.session.commit()

            # Retrieve and verify
            retrieved_task = Task.query.filter_by(title='Model Test Task').first()
            assert retrieved_task is not None
            assert retrieved_task.description == 'Testing the task model'
            assert retrieved_task.status == 'Pending'

    def test_user_task_relationship(self, app, auth_user, sample_task_data):
        """Test relationship between User and Task models"""
        with app.app_context():
            user = User.query.get(auth_user)

            # Create tasks for user
            task1 = Task(user_id=user.id, title='Task 1', status='Pending')
            task2 = Task(user_id=user.id, title='Task 2', status='Completed')
            db.session.add_all([task1, task2])
            db.session.commit()

            # Verify relationship
            user_tasks = Task.query.filter_by(user_id=user.id).all()
            assert len(user_tasks) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])