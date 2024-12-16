"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Planet, People, Favorite
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


# GETTERS

@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    return jsonify([people.serialize() for people in all_people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person_by_id(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({'Error':'Person not found'}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'Error':'Planet not found'}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users],), 200

@app.route('/users/favorites', methods=['GET'])
def get_favorites():
    try:
        fav = Favorite.query.all()
        if len(fav) <1:
            return jsonify({"msg": "No favorites found"}), 404
        s_fav = list(map(lambda x: x.serialize(), fav))
        return jsonify(s_fav), 200
    except Exception as e:
        return str(e), 500



#POST

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def post_favorite_planet(planet_id):
    body = request.json
    email = body.get("email")
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify({"msg":"No existe el usuario"}), 404
    
    planeta = Planet.query.get(planet_id)
    if planeta == None:
        return jsonify({"msg":"No existe el planeta"}), 404

    new_favorite = Favorite()
    new_favorite.user = user
    new_favorite.planet = planeta
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 200


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def post_favorite_people(people_id):
    body = request.json
    email = body.get("email")
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify({"msg":"No existe el usuario"}), 404
    
    personaje = People.query.get(people_id)
    if personaje == None:
        return jsonify({"msg":"No existe el personaje"}), 404

    new_favorite = Favorite()
    new_favorite.user = user
    new_favorite.people = personaje
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 200



#DELETE

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    body = request.json
    email = body.get("email")
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify({"msg":"No existe el usuario"}), 404
    
    planeta = Planet.query.get(planet_id)
    if planeta == None:
        return jsonify({"msg":"No existe el planeta"}), 404

    favorite_to_delete = Favorite.query.filter_by(user_id=user.id, planet_id=planeta.id).first()
    if favorite_to_delete == None:
        return jsonify({"msg":"No existe el planeta favorito"}), 404

    db.session.delete(favorite_to_delete)
    db.session.commit()

    return jsonify({"msg":"Eliminado con éxito"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    body = request.json
    email = body.get("email")
    user = User.query.filter_by(email=email).one_or_none()
    if user == None:
        return jsonify({"msg":"No existe el usuario"}), 404
    
    personaje = People.query.get(people_id)
    if personaje == None:
        return jsonify({"msg":"No existe el personaje"}), 404

    favorite_to_delete = Favorite.query.filter_by(user_id=user.id, people_id=personaje.id).first()
    if favorite_to_delete == None:
        return jsonify({"msg":"No existe el personaje favorito"}), 404

    db.session.delete(favorite_to_delete)
    db.session.commit()

    return jsonify({"msg":"Eliminado con éxito"}), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
