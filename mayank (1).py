# -*- coding: utf-8 -*-
"""Mayank.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bltzKs8zgDIeFsssvsyDscvIC9JoYWu_
"""

pip install Flask Flask-SQLAlchemy

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

"""create new points"""

@app.route('/v1/tasks', methods=['POST'])
def create_task():
    data = request.json
    if 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    new_task = Task(title=data['title'], is_completed=data.get('is_completed', False))
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"id": new_task.id}), 201

"""list all tasks"""

@app.route('/v1/tasks', methods=['GET'])
def list_tasks():
    tasks = Task.query.all()
    return jsonify({"tasks": [{"id": task.id, "title": task.title, "is_completed": task.is_completed} for task in tasks]}), 200

"""specific taks"""

@app.route('/v1/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
    if task is None:
        return jsonify({"error": "There is no task at that id"}), 404
    return jsonify({"id": task.id, "title": task.title, "is_completed": task.is_completed}), 200

"""Delete Tasks"""

@app.route('/v1/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return '', 204

"""edit task"""

@app.route('/v1/tasks/<int:id>', methods=['PUT'])
def edit_task(id):
    task = Task.query.get(id)
    if task is None:
        return jsonify({"error": "There is no task at that id"}), 404

    data = request.json
    if 'title' in data:
        task.title = data['title']
    if 'is_completed' in data:
        task.is_completed = data['is_completed']

    db.session.commit()
    return '', 204

"""Bulk ADD TASKS"""

@app.route('/v1/tasks/bulk', methods=['POST'])
def bulk_add_tasks():
    data = request.json
    tasks = data.get('tasks', [])

    created_tasks = []
    for task_data in tasks:
        if 'title' not in task_data:
            return jsonify({"error": "Title is required for each task"}), 400
        new_task = Task(title=task_data['title'], is_completed=task_data.get('is_completed', False))
        db.session.add(new_task)
        created_tasks.append({"id": new_task.id})

    db.session.commit()
    return jsonify({"tasks": created_tasks}), 201

"""bULK DELETE TAKS"""

@app.route('/v1/tasks/bulk', methods=['DELETE'])
def bulk_delete_tasks():
    data = request.json
    ids = data.get('ids', [])
    tasks = Task.query.filter(Task.id.in_(ids)).all()

    for task in tasks:
        db.session.delete(task)

    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)

!pip install pyngrok
from pyngrok import ngrok

from flask import Flask, jsonify, request
from pyngrok import ngrok

app = Flask(__name__)

# Set your ngrok authentication token
ngrok.set_auth_token("")

# Sample task list
tasks = []

@app.route('/v1/tasks', methods=['POST'])
def create_task():
    task = request.json
    task['id'] = len(tasks) + 1
    tasks.append(task)
    return jsonify({'id': task['id']}), 201

@app.route('/v1/tasks', methods=['GET'])
def list_tasks():
    return jsonify({'tasks': tasks}), 200

@app.route('/v1/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = next((task for task in tasks if task['id'] == id), None)
    if task is not None:
        return jsonify(task), 200
    return jsonify({'error': 'There is no task at that id'}), 404

@app.route('/v1/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    global tasks
    tasks = [task for task in tasks if task['id'] != id]
    return '', 204

@app.route('/v1/tasks/<int:id>', methods=['PUT'])
def edit_task(id):
    task = next((task for task in tasks if task['id'] == id), None)
    if task is None:
        return jsonify({'error': 'There is no task at that id'}), 404

    data = request.json
    task['title'] = data.get('title', task['title'])
    task['is_completed'] = data.get('is_completed', task['is_completed'])
    return '', 204

@app.route('/v1/tasks/bulk', methods=['POST'])
def bulk_add_tasks():
    new_tasks = request.json.get('tasks', [])
    for task in new_tasks:
        task['id'] = len(tasks) + 1
        tasks.append(task)
    return jsonify({'tasks': [{'id': task['id']} for task in new_tasks]}), 201

@app.route('/v1/tasks/bulk', methods=['DELETE'])
def bulk_delete_tasks():
    ids = request.json.get('ids', [])
    global tasks
    tasks = [task for task in tasks if task['id'] not in ids]
    return '', 204

# Start ngrok and the Flask app
if __name__ == '__main__':
    public_url = ngrok.connect(5000)
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:5000\"".format(public_url))
    app.run(port=5000)