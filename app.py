from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mroig:12345@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model): # child
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo ID: {self.id}, description: {self.description}, complete: {self.completed}>'

class TodoList(db.Model): # parent
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

    def __repr__(self):
        return f'<TodoList ID: {self.id}, name: {self.name}, todos: {self.todos}, completed: {self.completed}'

#! removed when using migrations
# with app.app_context():
#     db.create_all()

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {} # this body dictionary is used so we can return it after the session is closed, otherwise, the session objects (eg todo item) expire on commit
    try:
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        todo = Todo(description=description, completed=False, list_id=list_id)
        active_list = TodoList.query.get(list_id)
        todo.list = active_list
        db.session.add(todo)
        db.session.commit()
        body['id'] = todo.id
        body['description'] = todo.description
        body['completed'] = todo.completed
        body['list_id'] = todo.list_id
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)

@app.route('/lists/create', methods=['POST'])
def create_list():
    error = False
    body = {} 
    try:
        name = request.get_json()['name']
        list = TodoList(name=name)
        db.session.add(list)
        db.session.commit()
        body['id'] = list.id
        body['name'] = list.name
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
#* using parameter!
def set_completed_todo(todo_id):
    list_id = 0
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        list_id = todo.list_id
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('get_list_todos', list_id=list_id))

@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
    try:
        completed = request.get_json()['completed']
        list = TodoList.query.get(list_id)
        list.completed = completed
        for todo in list.todos:
            todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('get_list_todos', list_id=list_id))

@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def delete_item(todo_id):
    list_id = 0
    try:
        todo = Todo.query.filter_by(id=todo_id).first()
        list_id = todo.list_id
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('get_list_todos', list_id=list_id), 200)

@app.route('/lists/<list_id>/delete', methods=['DELETE'])
def delete_list(list_id):
    try:
        Todo.query.filter_by(list_id=list_id).delete()
        TodoList.query.filter_by(id=list_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('get_list_todos', list_id=list_id), 200)

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html', 
    lists=TodoList.query.all(), 
    active_list=TodoList.query.get(list_id), 
    todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())

@app.route('/')
# rendering an html file
def index():
    return redirect(url_for('get_list_todos', list_id=1))

# * to run with pyhton:
# if __name__ == "__main__":
    # app.run(debug=True)
