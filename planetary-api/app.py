# Import libraries


from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow 
from flask_jwt_extended import JWTManager, jwt_required, create_access_token


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +\
    os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'supersecret' # need change this

# Instancies


db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database create!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(
        planet_name='Mercury',
        planet_type='Class D',
        home_star='Sol',
        mass=3.258e23,
        radius=1516,
        distance=35.98e6
        )

    venus = Planet(
        planet_name='Venus',
        planet_type='Class K',
        home_star='Sol',
        mass=4.867e24,
        radius=3760,
        distance=67.24e6
        )

    earth = Planet(
        planet_name='Earth',
        planet_type='Class M',
        home_star='Sol',
        mass=5.972e24,
        radius=3959,
        distance=92.96e6
        )

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(
        first_name='jochimin',
        last_name='contreras',
        email='contrerasjochimin@gmail.com  ',
        password='123456789'
        )

    db.session.add(test_user)
    db.session.commit()
    print("Database seeded!")


@app.route('/')
def hello():
    return 'Hello World'


@app.route('/super_simple')
def super_simple():
    return jsonify(message='Hello from the Planetary API', zola=3+3), 200


@app.route('/not_found')
def not_found():
    return jsonify(message='Resource not found'), 404


# route with parameters http://localhost:5000/parameters?name=Jose&age=32
@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message='Sorry ' + name + ', you are not old enough')
    else:
        return jsonify(message='Hello ' + name + ', you are old enough')


# route with variables http://localhost:5000/url_variables/jochi/31
@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name: str, age: int):
    if age < 18:
        return jsonify(message='Sorry ' + name + ', you are not old enough')
    else:
        return jsonify(message='Hello ' + name + ', you are old enough')

# route to get all the planets


@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    results = planet_schema.dump(planets_list)
    return jsonify(results)


# route to register


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='This email already exists!')
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        #email = request.form['email']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully"), 201

# route to make login


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login succeeded!', access_token=access_token)
    else:
        return jsonify(message='Bad email or password'), 401


# database models


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(length=32))
    last_name = Column(String(length=50))
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String(length=50))
    planet_type = Column(String(length=50))
    home_star = Column(String(length=50))
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance')


user_schema = UserSchema()
user_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planet_schema = PlanetSchema(many=True)


if __name__ == "__main__":
    app.run(debug=True)