from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
api_key = "TopSecretAPIKey"
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")

## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(random_cafe.to_dict())


@app.route("/all")
def get_all():
    cafes = Cafe.query.all()
    # cafes_dict = {'cafes': [cafe.to_dict() for cafe in cafes]}
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route('/search')
def search():
    loc = request.args.get('loc')
    cafes = Cafe.query.filter_by(location=loc).all()
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


## HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_cafe():
    cafe = Cafe(
        name=request.form.get('name'),
        map_url=request.form.get('map_url'),
        img_url=request.form.get('img_url'),
        location=request.form.get('location'),
        seats=request.form.get('seats'),
        has_toilet=bool(request.form.get('has_toilet')),
        has_wifi=bool(request.form.get('has_wifi')),
        has_sockets=bool(request.form.get('has_sockets')),
        can_take_calls=bool(request.form.get('can_take_calls')),
        coffee_price=request.form.get('coffee_price')
    )
    db.session.add(cafe)
    db.session.commit()
    return jsonify(response={'Success': "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    updated_price = request.args.get('new_price')
    cafe = Cafe.query.get(cafe_id)
    cafe.coffee_price = updated_price
    db.session.commit()
    return jsonify(response={'Success': "Successfully added the new cafe."} if cafe else
    {'Error': 'Sorry a cafe with that id was not found in the database.'})


@app.route('/report-close/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    get_api = request.args.get('api-key')
    if get_api != api_key:
        return jsonify(response={'Forbidden': 'API-KEY is wrong. PleAse search with a correct API key'}), 403
    del_cafe = Cafe.query.get(cafe_id)
    if not del_cafe:
        return jsonify(response={'Not Found': 'No CAFE exists with such id'}), 404
    db.session.delete(del_cafe)
    db.session.commit()
    return jsonify(response={'Success': 'Cafe deleted successfully'}), 200


## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
