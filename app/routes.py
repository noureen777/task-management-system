
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from app import db
from app.models import Task, User, Category
from datetime import datetime

main = Blueprint('main', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)

    return decorated_function


# Auth Routes
@main.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')


@main.route('/register')
def register_page():
    return render_template('register.html')


@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.index'))
    return render_template('dashboard.html')


@main.route('/tasks')
def tasks_page():
    if 'user_id' not in session:
        return redirect(url_for('main.index'))
    return render_template('tasks.html')


@main.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'All fields are required'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    # Create default categories
    default_categories = [
        {'name': 'Work', 'color': '#0d6efd'},
        {'name': 'Personal', 'color': '#198754'},
        {'name': 'Shopping', 'color': '#ffc107'},
        {'name': 'Health', 'color': '#dc3545'}
    ]

    for cat_data in default_categories:
        category = Category(name=cat_data['name'], color=cat_data['color'], user_id=user.id)
        db.session.add(category)

    db.session.commit()

    session['user_id'] = user.id
    session['username'] = user.username

    return jsonify({'message': 'Registration successful', 'username': user.username}), 201


@main.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    session['user_id'] = user.id
    session['username'] = user.username

    return jsonify({'message': 'Login successful', 'username': user.username}), 200


@main.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200


# Category Routes
@main.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    return jsonify([cat.to_dict() for cat in categories])


@main.route('/api/categories', methods=['POST'])
@login_required
def create_category():
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'error': 'Category name is required'}), 400

    category = Category(
        name=data['name'],
        color=data.get('color', '#6c757d'),
        user_id=session['user_id']
    )

    db.session.add(category)
    db.session.commit()

    return jsonify(category.to_dict()), 201


@main.route('/api/categories/<int:id>', methods=['DELETE'])
@login_required
def delete_category(id):
    category = Category.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'}), 200


# Task Routes
@main.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    query = Task.query.filter_by(user_id=session['user_id'])

    # Search filter
    search = request.args.get('search')
    if search:
        query = query.filter(
            (Task.title.ilike(f'%{search}%')) |
            (Task.description.ilike(f'%{search}%'))
        )

    # Status filter
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    # Priority filter
    priority = request.args.get('priority')
    if priority:
        query = query.filter_by(priority=priority)

    # Category filter
    category_id = request.args.get('category_id')
    if category_id:
        query = query.filter_by(category_id=int(category_id))

    # Date filter
    overdue = request.args.get('overdue')
    if overdue == 'true':
        query = query.filter(Task.due_date < datetime.utcnow())

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])


@main.route('/api/tasks/<int:id>', methods=['GET'])
@login_required
def get_task(id):
    task = Task.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    return jsonify(task.to_dict())


@main.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        category_id=data.get('category_id'),
        user_id=session['user_id']
    )

    if data.get('due_date'):
        try:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


@main.route('/api/tasks/<int:id>', methods=['PUT'])
@login_required
def update_task(id):
    task = Task.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    data = request.get_json()

    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'category_id' in data:
        task.category_id = data['category_id']
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400
        else:
            task.due_date = None

    db.session.commit()

    return jsonify(task.to_dict())


@main.route('/api/tasks/<int:id>', methods=['DELETE'])
@login_required
def delete_task(id):
    task = Task.query.filter_by(id=id, user_id=session['user_id']).first_or_404()
    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully'}), 200


# Dashboard Stats
@main.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    user_id = session['user_id']

    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed = Task.query.filter_by(user_id=user_id, status='completed').count()
    pending = Task.query.filter_by(user_id=user_id, status='pending').count()
    in_progress = Task.query.filter_by(user_id=user_id, status='in-progress').count()

    overdue = Task.query.filter(
        Task.user_id == user_id,
        Task.due_date < datetime.utcnow(),
        Task.status != 'completed'
    ).count()

    high_priority = Task.query.filter_by(user_id=user_id, priority='high', status='pending').count()

    completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0

    # Tasks by category
    categories = Category.query.filter_by(user_id=user_id).all()
    tasks_by_category = []
    for cat in categories:
        count = Task.query.filter_by(user_id=user_id, category_id=cat.id).count()
        if count > 0:
            tasks_by_category.append({
                'name': cat.name,
                'count': count,
                'color': cat.color
            })

    return jsonify({
        'total_tasks': total_tasks,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'overdue': overdue,
        'high_priority': high_priority,
        'completion_rate': round(completion_rate, 1),
        'tasks_by_category': tasks_by_category
    })


