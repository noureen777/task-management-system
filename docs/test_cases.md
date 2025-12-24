# Test Cases for Task Management System

## Document Information
- **Project**: Task Management System
- **Version**: 1.0
- **Date**: December 24, 2025
- **Author**: Testing Team

---

## Table of Contents
1. [Authentication Test Cases](#authentication-test-cases)
2. [Task Creation Test Cases](#task-creation-test-cases)
3. [Task Retrieval Test Cases](#task-retrieval-test-cases)
4. [Task Update Test Cases](#task-update-test-cases)
5. [Task Deletion Test Cases](#task-deletion-test-cases)
6. [Category Management Test Cases](#category-management-test-cases)
7. [Dashboard Statistics Test Cases](#dashboard-statistics-test-cases)
8. [Security Test Cases](#security-test-cases)
9. [Integration Test Cases](#integration-test-cases)

---

## Authentication Test Cases

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|
| AUTH-001 | Successful user registration | Username: "newuser"<br>Email: "newuser@example.com"<br>Password: "password123" | Status: 201 Created<br>Message: "Registration successful"<br>User created in database<br>4 default categories created |
| AUTH-002 | Registration with duplicate username | Username: "existinguser" (already exists)<br>Email: "new@example.com"<br>Password: "password123" | Status: 400 Bad Request<br>Error: "Username already exists" |
| AUTH-003 | Registration with duplicate email | Username: "newuser2"<br>Email: "existing@example.com" (already exists)<br>Password: "password123" | Status: 400 Bad Request<br>Error: "Email already exists" |
| AUTH-004 | Registration with missing fields | Username: "incomplete"<br>Email: (empty)<br>Password: "password123" | Status: 400 Bad Request<br>Error: "All fields are required" |
| AUTH-005 | Successful user login | Username: "testuser"<br>Password: "testpassword123" | Status: 200 OK<br>Message: "Login successful"<br>Session created<br>Username returned |
| AUTH-006 | Login with invalid username | Username: "nonexistent"<br>Password: "password123" | Status: 401 Unauthorized<br>Error: "Invalid username or password" |
| AUTH-007 | Login with invalid password | Username: "testuser"<br>Password: "wrongpassword" | Status: 401 Unauthorized<br>Error: "Invalid username or password" |
| AUTH-008 | Login with missing credentials | Username: (empty)<br>Password: "password123" | Status: 400 Bad Request<br>Error: "Username and password are required" |
| AUTH-009 | Successful user logout | Authenticated session | Status: 200 OK<br>Message: "Logout successful"<br>Session cleared |
| AUTH-010 | Access protected route without authentication | No session/token | Status: 401 Unauthorized<br>Error: "Authentication required" |

---

## Task Creation Test Cases

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|
| TASK-001 | Create task with all fields | Title: "Test Task"<br>Description: "Task description"<br>Status: "pending"<br>Priority: "high"<br>Due Date: "2025-12-31"<br>Category ID: 1 | Status: 201 Created<br>Task object returned with all fields<br>Task saved in database |
| TASK-002 | Create task with minimal data | Title: "Minimal Task" | Status: 201 Created<br>Default status: "pending"<br>Default priority: "medium"<br>Description: "" (empty) |
| TASK-003 | Create task without authentication | Title: "Unauthorized Task"<br>(No session) | Status: 401 Unauthorized<br>Error: "Authentication required" |
| TASK-004 | Create task with missing title | Description: "No title task"<br>Status: "pending" | Status: 400 Bad Request<br>Error: "Title is required" |
| TASK-005 | Create task with invalid date format | Title: "Task"<br>Due Date: "31-12-2025" (wrong format) | Status: 400 Bad Request<br>Error: "Invalid date format" |
| TASK-006 | Create task with valid category | Title: "Work Task"<br>Category ID: 1 (Work) | Status: 201 Created<br>Task linked to category<br>Category ID in response |
| TASK-007 | Create task with invalid status | Title: "Task"<br>Status: "InvalidStatus" | Task created with default status "pending" or validation error |
| TASK-008 | Create task with invalid priority | Title: "Task"<br>Priority: "InvalidPriority" | Task created with default priority "medium" or validation error |
| TASK-009 | Create multiple tasks | 5 tasks with different titles | All 5 tasks created successfully<br>Each with unique ID |
| TASK-010 | Create task with past due date | Title: "Overdue Task"<br>Due Date: "2020-01-01" | Status: 201 Created<br>Task marked as overdue in stats |

---

## Task Retrieval Test Cases

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|
| RETR-001 | Get all tasks for authenticated user | Authenticated session | Status: 200 OK<br>Array of all user's tasks<br>Ordered by created_at DESC |
| RETR-002 | Get all tasks when none exist | Authenticated session<br>No tasks created | Status: 200 OK<br>Empty array [] |
| RETR-003 | Get all tasks without authentication | No session | Status: 401 Unauthorized<br>Error: "Authentication required" |
| RETR-004 | Get specific task by valid ID | Task ID: 1<br>Authenticated session | Status: 200 OK<br>Task object with matching ID |
| RETR-005 | Get task by non-existent ID | Task ID: 9999<br>Authenticated session | Status: 404 Not Found |
| RETR-006 | Get another user's task | Task ID: 5 (belongs to different user)<br>Authenticated session | Status: 404 Not Found<br>(User isolation enforced) |
| RETR-007 | Filter tasks by status | Query: ?status=pending<br>Authenticated session | Status: 200 OK<br>Only tasks with status "pending" |
| RETR-008 | Filter tasks by priority | Query: ?priority=high<br>Authenticated session | Status: 200 OK<br>Only tasks with priority "high" |
| RETR-009 | Filter tasks by category | Query: ?category_id=1<br>Authenticated session | Status: 200 OK<br>Only tasks in specified category |
| RETR-010 | Search tasks by title | Query: ?search=meeting<br>Authenticated session | Status: 200 OK<br>Tasks containing "meeting" in title or description |
| RETR-011 | Filter overdue tasks | Query: ?overdue=true<br>Authenticated session | Status: 200 OK<br>Only tasks with due_date < current date |
| RETR-012 | Combine multiple filters | Query: ?status=pending&priority=high<br>Authenticated session | Status: 200 OK<br>Tasks matching both criteria |

---

## Task Update Test Cases

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|
| UPD-001 | Update task with all fields | Task ID: 1<br>Title: "Updated Title"<br>Description: "Updated"<br>Status: "completed"<br>Priority: "low" | Status: 200 OK<br>Updated task object<br>Changes saved in database |
| UPD-002 | Partial update (status only) | Task ID: 1<br>Status: "completed" | Status: 200 OK<br>Only status updated<br>Other fields unchanged |
| UPD-003 | Update task without authentication | Task ID: 1<br>Title: "New Title"<br>(No session) | Status: 401 Unauthorized<br>Error: "Authentication required" |
| UPD-004 | Update non-existent task | Task ID: 9999<br>Title: "Updated"<br>Authenticated session | Status: 404 Not Found |
| UPD-005 | Update another user's task | Task ID: 5 (different user)<br>Title: "Updated"<br>Authenticated session | Status: 404 Not Found<br>(User isolation enforced) |
| UPD-006 | Update task title | Task ID: 1<br>Title: "New Task Title" | Status: 200 OK<br>Title updated successfully |
| UPD-007 | Update task description | Task ID: 1<br>Description: "New description" | Status: 200 OK<br>Description updated successfully |
| UPD-008 | Update task priority | Task ID: 1<br>Priority: "low" | Status: 200 OK<br>Priority updated successfully |
| UPD-009 | Update task due date | Task ID: 1<br>Due Date: "2026-01-15" | Status: 200 OK<br>Due date updated successfully |
| UPD-010 | Clear task due date | Task ID: 1<br>Due Date: null | Status: 200 OK<br>Due date set to null |
| UPD-011 | Update task category | Task ID: 1<br>Category ID: 2 | Status: 200 OK<br>Task moved to new category |
| UPD-012 | Mark task as complete | Task ID: 1<br>Status: "completed" | Status: 200 OK<br>Task status = "completed"<br>Stats updated |

---

## Task Deletion Test Cases

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|
| DEL-001 | Delete existing task | Task ID: 1<br>Authenticated session | Status: 200 OK<br>Message: "Task deleted successfully"<br>Task removed from database |
| DEL-002 | Delete task without authentication | Task ID: 1<br>(No session) | Status: 401 Unauthorized<br>Error: "Authentication required" |
| DEL-003 | Delete non-existent task | Task ID: 9999<br>Authenticated session | Status: 404 Not Found |
| DEL-004 | Delete another user's task | Task ID: 5 (different user)<br>Authenticated session | Status: 404 Not Found<br>(User isolation enforced) |
| DEL-005 | Verify task deletion | Task ID: 1 (after deletion)<br>GET request | Status: 404 Not Found<br>Task no longer exists |
| DEL-006 | Delete multiple tasks sequentially | Task IDs: 1, 2, 3<br>Authenticated session | All tasks deleted successfully<br>Each returns 200 OK |
| DEL-007 | Delete task with category | Task ID: 1 (has category)<br>Authenticated session | Status: 200 OK<br>Task deleted<br>Category remains |

---

## Category Management Test Cases

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|
| CAT-001 | Get all categories for user | Authenticated session | Status: 200 OK<br>Array of user's categories<br>(Default: 4 categories) |
| CAT-002 | Get categories without authentication | No session | Status: 401 Unauthorized<br>Error: "Authentication required" |
| CAT-003 | Create custom category | Name: "Custom Category"<br>Color: "#ff5733"<br>Authenticated session | Status: 201 Created<br>Category object returned<br>Category saved in database |
| CAT-004 | Create category without name | Color: "#ff5733"<br>(Name missing) | Status: 400 Bad Request<br>Error: "Category name is required" |
| CAT-005 | Delete existing category | Category ID: 1<br>Authenticated session | Status: 200 OK<br>Message: "Category deleted successfully"<br>Category removed from database |
| CAT-006 | Delete non-existent category | Category ID: 9999<br>Authenticated session | Status: 404 Not Found |
| CAT-007 | Delete another user's category | Category ID: 5 (different user)<br>Authenticated session | Status: 404 Not Found<br>(User isolation enforced) |
| CAT-008 | Verify default categories after registration | Register new user | 4 default categories created:<br>- Work (#0d6efd)<br>- Personal (#198754)<br>- Shopping (#ffc107)<br>- Health (#dc3545) |

---

## Dashboard Statistics Test Cases

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|
| STAT-001 | Get stats with no tasks | Authenticated session<br>No tasks created | Status: 200 OK<br>total_tasks: 0<br>completed: 0<br>pending: 0<br>completion_rate: 0 |
| STAT-002 | Get stats with tasks | Authenticated session<br>4 tasks: 2 completed, 1 pending, 1 in-progress | Status: 200 OK<br>total_tasks: 4<br>completed: 2<br>pending: 1<br>in_progress: 1<br>completion_rate: 50.0 |
| STAT-003 | Get stats without authentication | No session | Status: 401 Unauthorized<br>Error: "Authentication required" |
| STAT-004 | Verify overdue count | 3 tasks total<br>1 task overdue (past due date) | Status: 200 OK<br>overdue: 1 |
| STAT-005 | Verify high priority count | 5 tasks total<br>2 high priority pending | Status: 200 OK<br>high_priority: 2 |
| STAT-006 | Verify tasks by category | 3 categories with tasks<br>Work: 3, Personal: 2, Health: 1 | Status: 200 OK<br>tasks_by_category array with counts |
| STAT-007 | Verify completion rate calculation | 10 tasks total<br>7 completed | Status: 200 OK<br>completion_rate: 70.0 |
| STAT-008 | Stats reflect real-time changes | Create 1 task<br>Get stats<br>Complete task<br>Get stats | First stats: completed: 0<br>Second stats: completed: 1<br>Completion rate updated |

---

## Security Test Cases

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|
| SEC-001 | User cannot view other user's tasks | User A logged in<br>Request User B's task | Status: 404 Not Found<br>User isolation enforced |
| SEC-002 | User cannot update other user's tasks | User A logged in<br>Update User B's task | Status: 404 Not Found<br>No changes made |
| SEC-003 | User cannot delete other user's tasks | User A logged in<br>Delete User B's task | Status: 404 Not Found<br>Task remains |
| SEC-004 | User cannot view other user's categories | User A logged in<br>GET categories | Status: 200 OK<br>Only User A's categories returned |
| SEC-005 | User cannot delete other user's categories | User A logged in<br>Delete User B's category | Status: 404 Not Found<br>Category remains |
| SEC-006 | Session expires after logout | Login<br>Logout<br>Access protected route | Status: 401 Unauthorized<br>Session cleared |
| SEC-007 | Password is hashed in database | Register user with password: "password123" | Password stored as hash<br>Original password not retrievable |
| SEC-008 | SQL injection attempt in search | Search: "'; DROP TABLE tasks; --" | No SQL injection executed<br>Treated as search text<br>No database damage |
| SEC-009 | XSS attempt in task title | Title: "<script>alert('XSS')</script>" | Script not executed<br>Stored as text<br>Sanitized on display |
| SEC-010 | CSRF protection on state-changing operations | POST request without CSRF token<br>(if CSRF enabled) | Request rejected or CSRF handled |

---

## Integration Test Cases

| Test ID | Description | Input | Expected Output |
|---------|-------------|-------|-----------------|
| INT-001 | Complete task lifecycle (CRUD) | 1. Create task<br>2. Read task<br>3. Update task<br>4. Delete task | All operations successful<br>Task created → updated → deleted |
| INT-002 | User registration to task creation | 1. Register user<br>2. Login<br>3. Create task<br>4. View dashboard | All operations successful<br>User can manage tasks immediately |
| INT-003 | Task filtering and search workflow | 1. Create 10 tasks (various statuses/priorities)<br>2. Filter by status<br>3. Search by keyword<br>4. Apply multiple filters | Correct tasks returned for each query |
| INT-004 | Category management workflow | 1. Create custom category<br>2. Create task with category<br>3. View tasks by category<br>4. Delete category | Category created and used<br>Tasks filtered correctly |
| INT-005 | Multi-user isolation | 1. User A creates tasks<br>2. User B logs in<br>3. User B views tasks | User B sees 0 tasks<br>Complete data isolation |
| INT-006 | Dashboard stats accuracy | 1. Create 5 tasks (different statuses)<br>2. View dashboard<br>3. Complete 2 tasks<br>4. View dashboard again | Stats accurate after each change<br>Completion rate updates |
| INT-007 | Task status progression | 1. Create task (pending)<br>2. Update to in-progress<br>3. Update to completed | Status changes reflected<br>Stats update accordingly |
| INT-008 | Overdue task detection | 1. Create task with past due date<br>2. Get stats<br>3. Filter overdue tasks | Task marked as overdue<br>Appears in overdue filter |
| INT-009 | Session persistence | 1. Login<br>2. Create task<br>3. Refresh page<br>4. Create another task | Session maintained<br>Both tasks created successfully |
| INT-010 | Bulk operations | 1. Create 20 tasks<br>2. Filter by status<br>3. Update multiple tasks<br>4. Delete multiple tasks | All operations handle bulk correctly<br>No performance issues |

---

## Test Execution Summary

### Priority Levels
- **P1 (Critical)**: Must pass before release - Core functionality
- **P2 (High)**: Important features - Should pass before release
- **P3 (Medium)**: Nice to have - Can be fixed in next release
- **P4 (Low)**: Edge cases - Can be deferred

### Test Priority Mapping

| Category | Test IDs | Priority |
|----------|----------|----------|
| Authentication | AUTH-001, AUTH-005, AUTH-009 | P1 |
| Authentication | AUTH-002, AUTH-006, AUTH-010 | P2 |
| Task Creation | TASK-001, TASK-002, TASK-004 | P1 |
| Task Creation | TASK-005, TASK-006, TASK-007 | P2 |
| Task Retrieval | RETR-001, RETR-004, RETR-007 | P1 |
| Task Retrieval | RETR-010, RETR-011, RETR-012 | P2 |
| Task Update | UPD-001, UPD-002, UPD-012 | P1 |
| Task Deletion | DEL-001, DEL-005 | P1 |
| Categories | CAT-001, CAT-003, CAT-005 | P2 |
| Dashboard Stats | STAT-001, STAT-002, STAT-007 | P2 |
| Security | SEC-001, SEC-002, SEC-003, SEC-007 | P1 |
| Integration | INT-001, INT-002, INT-005 | P1 |

---

## Test Environment

### Prerequisites
- Python 3.12+
- Flask application running
- SQLite database (in-memory for testing)
- pytest and pytest-flask installed

### Test Execution Commands

```bash
# Run all tests
pytest tests/test_tasks.py -v

# Run specific test class
pytest tests/test_tasks.py::TestAuthentication -v

# Run with coverage
pytest tests/test_tasks.py --cov=app --cov-report=html -v

# Run priority 1 tests only (using markers)
pytest tests/test_tasks.py -m "priority1" -v
```

---

## Test Results Template

| Test ID | Status | Execution Date | Executed By | Notes |
|---------|--------|----------------|-------------|-------|
| AUTH-001 | ✅ Pass | 2025-12-24 | Tester | - |
| AUTH-002 | ✅ Pass | 2025-12-24 | Tester | - |
| ... | ... | ... | ... | ... |

---

## Defect Tracking

| Defect ID | Test ID | Severity | Description | Status | Assigned To |
|-----------|---------|----------|-------------|--------|-------------|
| DEF-001 | TASK-005 | Medium | Invalid date format returns 200 instead of 400 | Open | Dev Team |
| DEF-002 | SEC-009 | High | XSS vulnerability in task title | Fixed | Security Team |

---

## Notes
- All tests assume a clean database state at the start of each test
- Tests use in-memory SQLite database to avoid conflicts
- Authentication is session-based with user_id stored in session
- All API endpoints use JSON format for requests and responses
- Date format: YYYY-MM-DD (ISO 8601)
- Task statuses: pending, in-progress, completed (lowercase)
- Task priorities: low, medium, high (lowercase)

---

**Document Version**: 1.0  
**Last Updated**: December 24, 2025  
**Total Test Cases**: 95