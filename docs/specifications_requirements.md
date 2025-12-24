# Software Requirements Specification (SRS)
## Task Management Web Application

**Version:** 1.0  
**Date:** December 24, 2025  
**Prepared by:** Development Team

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification document describes the functional and non-functional requirements for the Task Management Web Application. The document is intended for developers, testers, project managers, and stakeholders involved in the development and deployment of the system.

### 1.2 Scope
The Task Management Web Application is a lightweight, single-user web-based system designed to help individuals organize, track, and manage their daily tasks efficiently. The system provides basic CRUD operations for task management with priority levels, status tracking, and timestamps.

### 1.3 Definitions, Acronyms, and Abbreviations
- **SRS:** Software Requirements Specification
- **CRUD:** Create, Read, Update, Delete
- **API:** Application Programming Interface
- **REST:** Representational State Transfer
- **UI:** User Interface
- **HTTP:** Hypertext Transfer Protocol
- **SQLite:** Structured Query Language Database

### 1.4 References
- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://www.sqlalchemy.org/
- Bootstrap Documentation: https://getbootstrap.com/
- REST API Design Standards: RFC 7231

### 1.5 Overview
This document is organized into sections covering system overview, functional requirements, non-functional requirements, system constraints, and assumptions. Each requirement is uniquely identified and prioritized.

---

## 2. System Overview

### 2.1 System Description
The Task Management Web Application is a client-server system built using Flask framework for the backend and Bootstrap for the frontend. It enables users to create, view, update, and delete tasks through an intuitive web interface. All task data is persisted in a local SQLite database.

### 2.2 System Architecture
The application follows a three-tier architecture:

**Presentation Layer:**
- HTML5, CSS3, JavaScript (ES6+)
- Bootstrap 5.3 for responsive UI
- Fetch API for asynchronous communication

**Application Layer:**
- Flask web framework (Python)
- RESTful API endpoints
- Business logic processing

**Data Layer:**
- SQLite relational database
- SQLAlchemy ORM
- Data persistence and retrieval

### 2.3 User Characteristics
The primary users are individuals seeking a simple task management solution. Users are expected to have:
- Basic computer literacy
- Familiarity with web browsers
- Understanding of task management concepts
- No technical expertise required

### 2.4 Operating Environment
- **Server-side:** Python 3.8 or higher
- **Client-side:** Modern web browsers (Chrome, Firefox, Safari, Edge)
- **Database:** SQLite 3.x
- **Network:** HTTP/HTTPS protocol
- **Operating System:** Platform-independent (Windows, macOS, Linux)

---

## 3. Functional Requirements

### 3.1 Task Creation

**FR-1.1: Create New Task**
- **Priority:** High
- **Description:** The system shall allow users to create new tasks with specified attributes.
- **Input:** Title (required), Description (optional), Status, Priority
- **Process:** Validate input, assign unique ID, store in database with timestamp
- **Output:** Success confirmation and display of newly created task
- **Acceptance Criteria:**
  - Title field must not be empty
  - Task is assigned a unique identifier
  - Creation timestamp is automatically generated
  - Task appears in the task list immediately

**FR-1.2: Task Title Validation**
- **Priority:** High
- **Description:** The system shall validate that task title is not empty and does not exceed 200 characters.
- **Input:** Task title string
- **Process:** Check for null/empty values and length constraints
- **Output:** Error message if validation fails

**FR-1.3: Default Values**
- **Priority:** Medium
- **Description:** The system shall assign default values for optional fields.
- **Default Values:**
  - Status: "pending"
  - Priority: "medium"
  - Description: empty string

### 3.2 Task Retrieval

**FR-2.1: Display All Tasks**
- **Priority:** High
- **Description:** The system shall display all tasks in descending order of creation date.
- **Input:** HTTP GET request to /api/tasks
- **Process:** Query database, serialize to JSON
- **Output:** Array of task objects with all attributes
- **Acceptance Criteria:**
  - All tasks are retrieved from database
  - Tasks are ordered by creation date (newest first)
  - Response time is under 2 seconds

**FR-2.2: Display Individual Task**
- **Priority:** Medium
- **Description:** The system shall retrieve and display details of a specific task by ID.
- **Input:** Task ID
- **Process:** Query database by ID
- **Output:** Single task object or 404 error
- **Acceptance Criteria:**
  - Valid ID returns complete task details
  - Invalid ID returns appropriate error message

**FR-2.3: Task Counter**
- **Priority:** Low
- **Description:** The system shall display the total number of tasks.
- **Input:** Task list
- **Process:** Count array length
- **Output:** Numeric count displayed in UI

### 3.3 Task Update

**FR-3.1: Edit Existing Task**
- **Priority:** High
- **Description:** The system shall allow users to modify existing task attributes.
- **Input:** Task ID and updated field values
- **Process:** Validate input, update database record, refresh timestamp
- **Output:** Updated task object
- **Acceptance Criteria:**
  - All fields can be individually updated
  - Updated timestamp reflects modification time
  - Changes persist after page refresh

**FR-3.2: Edit Mode UI**
- **Priority:** Medium
- **Description:** The system shall populate the form with existing task data when editing.
- **Input:** Task ID
- **Process:** Fetch task data, populate form fields
- **Output:** Pre-filled form with current values
- **Acceptance Criteria:**
  - Form title changes to "Edit Task"
  - Submit button text changes to "Update Task"
  - Cancel button becomes visible

**FR-3.3: Cancel Edit Operation**
- **Priority:** Medium
- **Description:** The system shall allow users to cancel edit operations.
- **Input:** Cancel button click
- **Process:** Reset form, clear edit state
- **Output:** Empty form in "Add" mode

### 3.4 Task Deletion

**FR-4.1: Delete Task**
- **Priority:** High
- **Description:** The system shall allow users to permanently delete tasks.
- **Input:** Task ID and user confirmation
- **Process:** Remove record from database
- **Output:** Confirmation message and updated task list
- **Acceptance Criteria:**
  - Confirmation dialog appears before deletion
  - Task is permanently removed from database
  - UI updates to reflect deletion

**FR-4.2: Deletion Confirmation**
- **Priority:** High
- **Description:** The system shall require explicit user confirmation before deleting a task.
- **Input:** Delete button click
- **Process:** Display confirmation dialog
- **Output:** Proceed with deletion or cancel operation

### 3.5 Task Attributes

**FR-5.1: Task Status**
- **Priority:** High
- **Description:** The system shall support three status values.
- **Valid Values:** "pending", "in-progress", "completed"
- **Default:** "pending"
- **Display:** Color-coded badges (yellow, blue, green)

**FR-5.2: Task Priority**
- **Priority:** Medium
- **Description:** The system shall support three priority levels.
- **Valid Values:** "low", "medium", "high"
- **Default:** "medium"
- **Display:** Color-coded badges (gray, blue, red)

**FR-5.3: Task Timestamps**
- **Priority:** Medium
- **Description:** The system shall automatically track creation and modification times.
- **Fields:**
  - created_at: Set on task creation
  - updated_at: Updated on any modification
- **Format:** YYYY-MM-DD HH:MM:SS

### 3.6 User Interface

**FR-6.1: Responsive Design**
- **Priority:** High
- **Description:** The system shall provide a responsive interface that adapts to different screen sizes.
- **Breakpoints:** Desktop (≥768px), Mobile (<768px)
- **Layout:** Two-column on desktop, single-column on mobile

**FR-6.2: Visual Feedback**
- **Priority:** Medium
- **Description:** The system shall provide visual feedback for user interactions.
- **Examples:**
  - Hover effects on task cards
  - Loading indicators during API calls
  - Color-coded status and priority badges

**FR-6.3: Real-time Updates**
- **Priority:** High
- **Description:** The system shall update the task list immediately after any CRUD operation.
- **Trigger:** After successful API response
- **Process:** Fetch updated task list, re-render UI
- **Output:** Current state of all tasks

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

**NFR-1.1: Response Time**
- **Description:** API endpoints shall respond within 2 seconds under normal load.
- **Measurement:** Time from request initiation to response completion
- **Target:** 95th percentile < 2 seconds

**NFR-1.2: Database Query Performance**
- **Description:** Database queries shall execute efficiently.
- **Target:** Single task retrieval < 100ms, All tasks retrieval < 500ms
- **Method:** Proper indexing on task ID

**NFR-1.3: Page Load Time**
- **Description:** Initial page load shall complete within 3 seconds.
- **Includes:** HTML, CSS, JavaScript, and external libraries
- **Network:** Assuming broadband connection (10+ Mbps)

### 4.2 Reliability Requirements

**NFR-2.1: Availability**
- **Description:** The system shall be available during server runtime.
- **Target:** 99% uptime during operational hours
- **Recovery:** Automatic restart on crash

**NFR-2.2: Data Integrity**
- **Description:** The system shall maintain data consistency.
- **Method:** Database transactions, foreign key constraints
- **Validation:** Input validation on both client and server

**NFR-2.3: Error Handling**
- **Description:** The system shall handle errors gracefully without crashing.
- **Coverage:** Network failures, invalid inputs, database errors
- **User Impact:** Clear error messages, no data loss

### 4.3 Usability Requirements

**NFR-3.1: Ease of Use**
- **Description:** Users shall perform common tasks with minimal training.
- **Target:** New users can create/edit/delete tasks within 5 minutes
- **Learning Curve:** Intuitive interface following web conventions

**NFR-3.2: Visual Clarity**
- **Description:** The interface shall clearly distinguish between different task states.
- **Method:** Color coding, iconography, clear labels
- **Accessibility:** Sufficient color contrast ratios

**NFR-3.3: Feedback Messages**
- **Description:** The system shall provide clear feedback for all user actions.
- **Types:** Success confirmations, error messages, loading indicators
- **Timing:** Immediate feedback for synchronous operations

### 4.4 Security Requirements

**NFR-4.1: Input Validation**
- **Description:** The system shall validate all user inputs on the server side.
- **Prevention:** SQL injection, XSS attacks, invalid data
- **Method:** ORM parameterized queries, HTML escaping

**NFR-4.2: Data Sanitization**
- **Description:** The system shall sanitize user inputs before display.
- **Method:** HTML entity encoding in JavaScript
- **Protection:** XSS prevention in dynamic content

**NFR-4.3: HTTP Method Security**
- **Description:** API endpoints shall only accept appropriate HTTP methods.
- **Enforcement:** Flask route decorators with method restrictions
- **Error:** 405 Method Not Allowed for incorrect methods

### 4.5 Maintainability Requirements

**NFR-5.1: Code Organization**
- **Description:** The codebase shall follow modular architecture.
- **Structure:** Separation of concerns (models, routes, templates)
- **Benefit:** Easy to understand, modify, and extend

**NFR-5.2: Documentation**
- **Description:** Code shall include inline comments and docstrings.
- **Coverage:** Complex functions, API endpoints, business logic
- **Format:** Python docstrings, JavaScript JSDoc comments

**NFR-5.3: Version Control**
- **Description:** All code changes shall be tracked in version control.
- **System:** Git recommended
- **Practice:** Meaningful commit messages, branching strategy

### 4.6 Portability Requirements

**NFR-6.1: Platform Independence**
- **Description:** The application shall run on multiple operating systems.
- **Supported:** Windows, macOS, Linux
- **Dependencies:** Python 3.8+, modern web browser

**NFR-6.2: Browser Compatibility**
- **Description:** The UI shall function correctly across major browsers.
- **Supported:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Features:** CSS Grid, Fetch API, ES6 JavaScript

**NFR-6.3: Database Portability**
- **Description:** SQLite database file shall be portable across systems.
- **Format:** Standard SQLite3 format
- **Location:** instance/ directory relative to application

### 4.7 Scalability Requirements

**NFR-7.1: Data Volume**
- **Description:** The system shall handle up to 10,000 tasks efficiently.
- **Performance:** No significant degradation in response time
- **Limitation:** Single-user system, not designed for concurrent users

**NFR-7.2: Future Extensibility**
- **Description:** Architecture shall allow for future enhancements.
- **Examples:** User authentication, task categories, due dates
- **Method:** Modular design, RESTful API structure

---

## 5. System Constraints

### 5.1 Technical Constraints

**C-1.1: Technology Stack**
- Backend must use Flask framework
- Database must be SQLite (no PostgreSQL/MySQL)
- Frontend must use Bootstrap 5.x
- ORM must be SQLAlchemy

**C-1.2: Single-User Limitation**
- No multi-user support or authentication
- No user sessions or access control
- Single SQLite database instance

**C-1.3: Browser Requirements**
- Requires JavaScript enabled
- Requires modern browser with ES6 support
- No Internet Explorer support

**C-1.4: Storage Limitations**
- SQLite database size limited by filesystem
- No cloud storage integration
- Local file system only

### 5.2 Design Constraints

**C-2.1: RESTful API**
- Must follow REST architectural principles
- JSON as data exchange format
- Standard HTTP methods and status codes

**C-2.2: Single-Page Application**
- No page reloads for CRUD operations
- Asynchronous communication via Fetch API
- Dynamic DOM manipulation

**C-2.3: Responsive Design**
- Must work on desktop and mobile devices
- Bootstrap grid system required
- Mobile-first approach

### 5.3 Operational Constraints

**C-3.1: Development Environment**
- Python 3.8 or higher required
- pip package manager for dependencies
- Local development server (Flask dev server)

**C-3.2: Deployment**
- Not production-ready (Flask debug mode)
- No WSGI server configuration
- No SSL/TLS encryption

**C-3.3: Backup and Recovery**
- No automated backup mechanism
- Manual database file backup required
- No disaster recovery procedures

---

## 6. Assumptions and Dependencies

### 6.1 Assumptions

**A-1.1: User Environment**
- Users have a modern web browser installed
- Users have stable internet connection for CDN resources
- Users have basic computer literacy

**A-1.2: System Resources**
- Sufficient disk space for database growth
- Adequate RAM for Python runtime (minimum 512MB)
- Network connectivity for external CDN resources

**A-1.3: Usage Patterns**
- Single user per application instance
- Moderate task creation rate (< 100 tasks/day)
- No concurrent access requirements

**A-1.4: Data Characteristics**
- Task titles are reasonably short (< 200 characters)
- Task descriptions are text-based (no rich media)
- Number of tasks remains under 10,000

### 6.2 Dependencies

**D-1.1: External Libraries**
- Flask: Web framework
- Flask-SQLAlchemy: ORM integration
- Bootstrap 5.3: UI framework (CDN)
- Python 3 standard library

**D-1.2: CDN Resources**
- Bootstrap CSS and JavaScript
- Internet connectivity required for CDN access
- Fallback mechanism not implemented

**D-1.3: Database**
- SQLite driver included in Python
- File system with write permissions
- No external database server required

**D-1.4: Runtime Environment**
- Python interpreter availability
- Flask development server
- Operating system file system access

---

## 7. Use Cases

### 7.1 UC-1: Create Task
**Actor:** User  
**Precondition:** Application is running, browser is open  
**Main Flow:**
1. User navigates to application homepage
2. User enters task title in the form
3. User optionally enters description
4. User selects status and priority
5. User clicks "Add Task" button
6. System validates input
7. System creates task in database
8. System displays success message
9. System updates task list

**Postcondition:** New task is visible in task list  
**Alternative Flow:**
- 6a. Title is empty → Display error message, return to step 2

### 7.2 UC-2: View Tasks
**Actor:** User  
**Precondition:** Application is running  
**Main Flow:**
1. User opens application
2. System fetches all tasks from database
3. System displays tasks in descending order
4. User views task details including title, description, status, priority, timestamps

**Postcondition:** User sees current list of all tasks  
**Alternative Flow:**
- 2a. No tasks exist → Display "No tasks yet" message

### 7.3 UC-3: Edit Task
**Actor:** User  
**Precondition:** At least one task exists  
**Main Flow:**
1. User clicks "Edit" button on a task
2. System loads task data into form
3. Form switches to edit mode
4. User modifies task attributes
5. User clicks "Update Task" button
6. System validates input
7. System updates task in database
8. System refreshes task list

**Postcondition:** Task is updated with new values  
**Alternative Flow:**
- 7a. Validation fails → Display error, return to step 4
- User clicks "Cancel" → Clear form, return to add mode

### 7.4 UC-4: Delete Task
**Actor:** User  
**Precondition:** At least one task exists  
**Main Flow:**
1. User clicks "Delete" button on a task
2. System displays confirmation dialog
3. User confirms deletion
4. System removes task from database
5. System updates task list

**Postcondition:** Task is permanently removed  
**Alternative Flow:**
- 3a. User cancels → No deletion occurs, return to task list

---

## 8. Data Requirements

### 8.1 Data Model

**Task Entity:**
| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique task identifier |
| title | String(200) | NOT NULL | Task title/summary |
| description | Text | NULL | Detailed task description |
| status | String(20) | NOT NULL, Default='pending' | Current task status |
| priority | String(20) | NOT NULL, Default='medium' | Task priority level |
| created_at | DateTime | NOT NULL, Auto-generated | Creation timestamp |
| updated_at | DateTime | NOT NULL, Auto-update | Last modification timestamp |

### 8.2 Data Validation Rules

**Title:**
- Required field
- Maximum length: 200 characters
- Minimum length: 1 character
- No special validation on content

**Description:**
- Optional field
- No maximum length constraint
- Stored as TEXT type
- Can contain newlines and special characters

**Status:**
- Must be one of: 'pending', 'in-progress', 'completed'
- Case-sensitive
- Default: 'pending'

**Priority:**
- Must be one of: 'low', 'medium', 'high'
- Case-sensitive
- Default: 'medium'

**Timestamps:**
- Automatically managed by system
- UTC timezone
- Format: YYYY-MM-DD HH:MM:SS
- Read-only from user perspective

### 8.3 Data Retention

- Tasks persist indefinitely until explicitly deleted
- No automatic archival or cleanup
- No soft-delete mechanism
- Database file grows with task additions

---

## 9. Interface Requirements

### 9.1 User Interface

**UI-1: Main Dashboard**
- Two-column layout on desktop
- Left column: Task creation/edit form
- Right column: Task list
- Navigation bar with application title
- Responsive collapse on mobile

**UI-2: Task Form**
- Title input field (text)
- Description textarea (multi-line)
- Status dropdown (3 options)
- Priority dropdown (3 options)
- Submit button (Add/Update)
- Cancel button (visible in edit mode)

**UI-3: Task List**
- Scrollable container
- Individual task cards
- Color-coded borders by status
- Priority and status badges
- Timestamp display
- Edit and Delete buttons per task
- Task count badge in header

### 9.2 API Interface

**API-1: GET /api/tasks**
- Returns: Array of task objects
- Status: 200 OK
- Content-Type: application/json

**API-2: GET /api/tasks/{id}**
- Returns: Single task object
- Status: 200 OK | 404 Not Found
- Content-Type: application/json

**API-3: POST /api/tasks**
- Request Body: Task object (without id)
- Returns: Created task object
- Status: 201 Created | 400 Bad Request
- Content-Type: application/json

**API-4: PUT /api/tasks/{id}**
- Request Body: Task object (partial updates allowed)
- Returns: Updated task object
- Status: 200 OK | 404 Not Found | 400 Bad Request
- Content-Type: application/json

**API-5: DELETE /api/tasks/{id}**
- Returns: Success message
- Status: 200 OK | 404 Not Found
- Content-Type: application/json

---

## 10. Appendices

### 10.1 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-24 | Development Team | Initial release |

### 10.2 Glossary

**Task:** A single unit of work with title, description, status, and priority  
**CRUD:** Create, Read, Update, Delete operations  
**REST API:** Representational State Transfer Application Programming Interface  
**ORM:** Object-Relational Mapping  
**CDN:** Content Delivery Network  
**SQLite:** Lightweight relational database management system  

### 10.3 Future Enhancements

The following features may be considered for future versions:
- User authentication and authorization
- Task categories and tags
- Due dates and reminders
- Task search and filtering
- Data export (CSV, PDF)
- Multiple user support
- Cloud synchronization
- Mobile native applications
- Task attachments
- Recurring tasks
- Task comments and notes
- Activity logging and audit trail

---

**Document End**