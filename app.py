from flask import Flask, render_template, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://cameron:postgres@localhost:5432/todoapp'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'


#Anti-pattern when using migrations
#migrations perform same function but with added 
#benefit of tracking versions to enable rollbacks
#db.create_all()

#flask migrate command creates the migration file and tracks changes
#flask upgrade runs the instructions in that file to implement those changes

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort (400)
    else:
        #!cannot access todo object directly after closing the session
        #!because it could have been modified since the session was closed
        #!so we copied the description key to a blank object called body
        #!this ensures we always know the state of the data before returning it
        return jsonify(body)        

@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())