from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://@localhost:3309/db_demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app=app)
ma = Marshmallow(app=app)

# Client Class/Model
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def __init__(self, name):
        self.name = name


@app.route('/', methods=['GET'])
def get():
    return jsonify({'msg': 'Ola Vivi!!'})

# Run server
if __name__ == '__main__':
    app.run(debug=True)

