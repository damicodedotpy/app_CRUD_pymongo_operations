from flask import Flask, request, jsonify, Response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb://localhost:27017/flask_mongodb'
mongo = PyMongo(app)

@app.route('/users', methods=["POST"])
def create_user():
    username = request.json["username"]
    password = request.json["password"]
    email = request.json["email"]

    if username and password and email:
        hashed_password = generate_password_hash(password)

        # Esto lo que dice es 'En mongo, en una base de datos, en una coleccion llamada 'users' vas a insertas el siguiente objeto
        id = mongo.db.users.insert_one(
            {
                "username": username,
                "password": hashed_password,
                "email": email
            }
        )
        response = {
            "id": str(id),
            "username": username,
            "password": hashed_password,
            "email": email
        }
        return response
    else:
        return not_found()
    return {"message": "Recibido"}

@app.route("/users", methods=["GET"])
def get_users():
    users = mongo.db.users.find()
    response = json_util.dumps(users)
    return Response(response, mimetype="application/json")


@app.route("/users/<string:id>", methods=["GET"])
def get_user(id):
    user = mongo.db.users.find_one({"_id": ObjectId(id)})
    response = json_util.dumps(user)
    return Response(response, mimetype="application/json")

@app.route("/users/<string:id>", methods=["DELETE"])
def delete_user(id):
    print(id)
    mongo.db.users.delete_one({'_id': ObjectId(id)})
    response = jsonify({"message": f"User {id} was deleted successfully"})
    return response

@app.route("/users/<string:id>", methods=["PUT"])
def update_user(id):
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    if username and email and password:
        hashed_password = generate_password_hash(password)
        mongo.db.users.update_one({'_id':ObjectId(id)}, {"$set": {
            "username": username,
            "password": hashed_password,
            "email": email
        }})
        response = jsonify({"message": f"User {id} was updated successfully"})
        return response

@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        "message": "Resource not found" + request.url,
        "status": 404
    })
    response.status_code = 404
    return response

if __name__ == "__main__":
    app.run(debug=True)