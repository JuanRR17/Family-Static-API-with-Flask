"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
last_name = "Jackson"
_members = [
            {
                "first_name": "John",
                "age": 33,
                "lucky_numbers": [7,13,22]
            },
            {
                "first_name": "Jane",
                "age": 35,
                "lucky_numbers": [10,14,3]
            },
            {
                "first_name": "Jimmy",
                "age": 5,
                "lucky_numbers": [1]
            }]
jackson_family = FamilyStructure(last_name)
for member in _members:
    jackson_family.add_member(member)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Get all members
@app.route('/members', methods=['GET'])
def handle_hello():

    # this is how you can use the Family datastructure by calling its methods
    try:
        jackson_family
    except NameError:
        return jsonify({"msg":"Family doesnt exist"}),500
    else:
        members = jackson_family.get_all_members()
        return jsonify(members), 200

# Get one member
@app.route('/member/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        jackson_family
    except NameError:
        return jsonify({"msg":"Family doesnt exist"}),500
    
    member = jackson_family.get_member(member_id)
    if member:
        return jsonify(member),200
    else:
        return jsonify({"msg":"Member doesnt exist"}),400


# Add member
@app.route('/member', methods=['POST'])
def add_member():
    try:
        jackson_family
    except NameError:
        return jsonify({"msg":"Family doesnt exist"}),500

    response_body = request.get_json()

    # Handling first_name errors
    try:
        first_name = response_body["first_name"]
        if not isinstance(first_name, str):
            raise ValueError()
    except KeyError:
        return jsonify({"msg":"first_name key must be entered"}),400
    except ValueError:
        return jsonify({"msg":"first_name must be a string"}),400

    # Handling age errors
    try:
        age = int(response_body["age"])
        if age < 0:
            raise Exception()
    except KeyError:
        return jsonify({"msg":"Age key must be entered"}),400
    except ValueError:
        return jsonify({"msg":"Age value must be an integer"}),400
    except Exception:
        return jsonify({"msg":"Age can't be negative"}),400

    # Handling lucky_numbers errors
    try:
        lucky_numbers = response_body["lucky_numbers"]
        if not isinstance(lucky_numbers, list):
            raise ValueError()
    except KeyError:
        return jsonify({"msg":"lucky_numbers key must be entered"}),400
    except ValueError:
        return jsonify({"msg":"lucky_numbers must be a list"}),400

    # Creating new member
    new_member = {
        "first_name": first_name,
        "age": age,
        "lucky_numbers": lucky_numbers
    }
    # Adding id if it has been entered
    if "id" in response_body.keys():
        try: 
            id = response_body["id"]
            new_member["id"] = int(id)
        except ValueError:
            return jsonify({"msg":"id is not a number"}),400
            
    jackson_family.add_member(new_member)
    return ({"":""}, 200)

# Delete member
@app.route('/member/<int:id>', methods=['DELETE'])
def delete_member(id):
    try:
        jackson_family
    except NameError:
        return jsonify({"msg":"Family doesnt exist"}),500

    if jackson_family.delete_member(id):
        return jsonify({"done":True}), 200
    else:
        return jsonify({"msg":"Member not found"}),404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
