from ast import Or
import json
import psycopg2
from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow

from db import *
from models.user import users_schema, Users, user_schema
from models.org import Organizations, organizations_schema, organization_schema

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://sarahroy@localhost:5432/alchemy"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app, db)
ma = Marshmallow(app)

def create_all():
  with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("All done!")

def populate_object(obj, data_dictionary):
  fields = data_dictionary.keys()
  for field in fields:
    if getattr(obj, field): 
      setattr(obj, field, data_dictionary[field])
    
@app.route('/user/add', methods=['POST'] )
def user_add():
  post_data = request.json
  
  if not post_data:
    post_data = request.post
  
  first_name = post_data.get('first_name')
  last_name = post_data.get('last_name')
  email = post_data.get('email')
  phone = post_data.get('phone')
  city = post_data.get('city')
  state = post_data.get('state')
  org_id = post_data.get('org_id')
  active = post_data.get('active')

  add_user(first_name, last_name, email, phone, city, state, org_id, active)

  return jsonify("User created"), 201

def add_user(first_name, last_name, email, phone, city, state, org_id, active): 
  new_user = Users(first_name, last_name, email, phone, city, state, org_id, active)
  
  db.session.add(new_user)
  db.session.commit()

@app.route('/org/add', methods=['POST'] )
def org_add():
  post_data = request.json
  if not post_data:
    post_data = request.form
  name = post_data.get('name')
  phone = post_data.get('phone')
  city = post_data.get('city')
  state = post_data.get('state')
  active = post_data.get('active')

  add_org(name, phone, city, state, active)

  return jsonify("Org created"), 201

def add_org(name, phone, city, state, active):
  new_org = Organizations(name, phone, city, state, active)
  db.session.add(new_org)
  db.session.commit()

@app.route('/user_by_id/get/<user_id>', methods=['GET'] )
def get_user_by_id(user_id):
  results = db.session.query(Users).filter(Users.user_id == user_id).first()

  if results:
    return jsonify(user_schema.dump(results)), 200
  
  else:
    return jsonify('No Users Found'), 404

@app.route('/org_by_id/<org_id>', methods=['GET'] )
def get_org_by_id(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

  if results:
    return jsonify(organization_schema.dump(results)), 200
  
  else:
    return jsonify('No Organization Found'), 404	

@app.route('/users/get', methods=['GET'] )
def get_all_active_users():
  results = db.session.query(Users).filter(Users.active == True).all()

  if results:
    return jsonify(users_schema.dump(results)), 200
  
  else:
    return jsonify('No Users Found'), 404

@app.route('/org/get', methods=[('GET')])
def get_all_active_orgs():
  results = db.session.query(Organizations).filter(Organizations.active == True).all()

  if results:
    return jsonify(organizations_schema.dump(results)), 200
  
  else:
    return jsonify('No Organization Found'), 404	
    
@app.route('/user/update/<user_id>', methods=['POST', 'PUT'] )
def edit_user(user_id, first_name = None, last_name = None, email = None, password = None, city = None, state = None, active = None):
  user_record = db.session.query(Users).filter(Users.user_id == user_id).first()

  new_data = request.form if request.form else request.json

  if new_data:
    new_data = dict(new_data)
  else:
    return jsonify("No values to change")

  if not user_record:
    return('User not found'), 404

  populate_object(user_record, new_data)
  db.session.commit()

  return jsonify('User Updated'), 201

@app.route('/org/update/<org_id>', methods=['POST', 'PUT'] )
def edit_org(org_id, name = None, phone=None, city = None, state = None, active = None):
  org_record = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()

  new_data = request.form if request.form else request.json

  if new_data:
    new_data = dict(new_data)
  else:
    return jsonify("No values to change")

  if not org_record:
    return('User not found'), 404

  populate_object(org_record, new_data)
  db.session.commit()

  return jsonify('Organization Updated'), 201

@app.route('/user/activate/<user_id>', methods=['GET'] )
def user_activate(user_id):
  results = db.session.query(Users).filter(Users.user_id == user_id).first()
  results.active=True
  db.session.commit()
  return jsonify('User Activated'), 200

@app.route('/org/activate/<org_id>', methods=['GET'] )
def org_activate(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  results.active=True
  db.session.commit()
  return jsonify('Organization Activated'), 200

@app.route('/user/deactivate/<user_id>', methods=['GET'] )
def user_deactivate(user_id):
  results = db.session.query(Users).filter(Users.user_id == user_id).first()
  results.active=False
  db.session.commit()
  return jsonify('User Deactivated'), 200

@app.route('/org/deactivate/<org_id>', methods=['GET'] )
def org_deactivate(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  results.active=False
  db.session.commit()
  return jsonify('Organization Deactivated'), 200

@app.route('/user/delete/<user_id>', methods=['DELETE'] )
def user_delete(user_id):
  results = db.session.query(Users).filter(Users.user_id == user_id).first()
  db.session.delete(results)
  db.session.commit()
  return jsonify('User Deleted'), 200

@app.route('/org/delete/<org_id>', methods=['DELETE'] )
def org_delete(org_id):
  results = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  db.session.delete(results)
  db.session.commit()
  return jsonify('Organization Deleted'), 200

if __name__ == '__main__':
  create_all()
  app.run(host='0.0.0.0', port="4000")