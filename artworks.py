from flask import Blueprint, request, jsonify
from musemingle import db

artworks_bp = Blueprint('artworks', __name__)

class Artworks(db.Model):
    __tablename__ = 'Artworks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creation_date = db.Column(db.Date, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

@artworks_bp.route('/artworks', methods=['GET'])
def get_artworks():
    artworks = Artworks.query.all()
    return jsonify([artwork.as_dict() for artwork in artworks])

@artworks_bp.route('/artworks', methods=['POST'])
def create_artwork():
    new_artwork = Artworks(**request.json)
    db.session.add(new_artwork)
    db.session.commit()
    return jsonify(new_artwork.as_dict()), 201

@artworks_bp.route('/artworks/<int:artwork_id>', methods=['GET'])
def get_artwork(artwork_id):
    artwork = Artworks.query.get_or_404(artwork_id)
    return jsonify(artwork.as_dict())

@artworks_bp.route('/artworks/<int:artwork_id>', methods=['PUT'])
def update_artwork(artwork_id):
    artwork = Artworks.query.get_or_404(artwork_id)
    db.session.commit()
    return jsonify(artwork.as_dict())

@artworks_bp.route('/artworks/<int:artwork_id>', methods=['DELETE'])
def delete_artwork(artwork_id):
    artwork = Artworks.query.get_or_404(artwork_id)
    db.session.delete(artwork)
    db.session.commit()
    return '', 204

# Helper method to serialize the Artworks object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the Artworks class
Artworks.as_dict = as_dict
