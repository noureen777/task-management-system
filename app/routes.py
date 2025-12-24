from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Task

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

@main.route('/api/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get_or_404(id)
    return jsonify(task.to_dict())

@main.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium')
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

@main.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    
    db.session.commit()
    
    return jsonify(task.to_dict())

@main.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'}), 200