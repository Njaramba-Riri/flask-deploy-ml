import numpy as np
import pickle 

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields
import pymysql

app=Flask(__name__)

app.app_context()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/'

db = SQLAlchemy(app)

class Authors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    specialisation = db.Column(db.String(50))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def __init__(self, name, specialisation):
        self.name = name
        self.specialisation = specialisation

    def __repr__(self):
        return '<Author %d>' % self.id
    
db.create_all()



#Output Schema
class AuthorSchema(SQLAlchemySchema):
    class Meta(SQLAlchemySchema.Meta):
        model = Authors
        sqla_session = db.session
    
    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    specialisation = fields.String(required=True)


@app.route('/authors', methods = ['GET'])
def index():
    get_authors = Authors.query.all()
    author_schema = AuthorSchema(many=True)
    authors, error = author_schema.dump(get_authors)
    return make_response(jsonify({"authors":authors}))

@app.route('/authors/<id>', methods = ['GET'])
def get_author_by_id(id):
    get_author = Authors.query.get(id)
    author_schema = AuthorSchema()
    author, error = author_schema.dump(get_author)
    return make_response(jsonify({"author": author}))


@app.route('/authors/<id>', methods = ['PUT'])
def update_author_by_id(id):
    data = request.get_json()
    get_author = Authors.query.get(id)
    if data.get('specialisation'):
        get_author.specialisation = data['specialisation']
    if data.get('name'):
        get_author.name = data['name']

    db.session.add(get_author)
    db.session.commit()
    author_schema = AuthorSchema(only=['id', 'name', 'specialisation'])
    author, error = author_schema.dump(get_author)
    return make_response(jsonify({"author": author}))


@app.route('/authors', methods = ['POST'])
def create_author():
    data = request.get_json()
    author_schema = AuthorSchema()
    author, error = author_schema.load(data)
    result = author_schema.dump(author.create())
    return make_response(jsonify({"author":  author}), 200)


@app.route('/authors/<id>', methods = ['DELETE'])
def remove_author_by_id(id):
    get_author = Authors.query.get(id)
    db.session.delete(get_author)
    db.session.commit()
    return make_response("", 204)


#load the model
model=pickle.load(open('model.pkl','rb'))

@app.route('/')
def home():
    return 'Hello there, This is My third Flask app.'

@app.route('/api',methods=['POST'])
def predict():
    #get data from post request
    data=request.get_json(force=True)
    #make prediction using model loaded from disk as per the data
    prediction=model.predict([[np.array(data['exp'])]])

    #take the first value of prediction
    output=prediction[0]
    return jsonify(output)


if __name__=='__main__':
    app.run(port=5000, debug=True)
