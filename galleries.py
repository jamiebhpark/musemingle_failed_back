from flask import Blueprint, request, jsonify
from musemingle import db

galleries_bp = Blueprint('galleries', __name__)

class Galleries(db.Model):
    __tablename__ = 'Galleries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    country = db.Column(db.String(255))
    zip_code = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean)
    website = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

@galleries_bp.route('/galleries', methods=['GET'])
def get_galleries():
    galleries = Galleries.query.all()
    return jsonify([gallery.as_dict() for gallery in galleries])

@galleries_bp.route('/galleries', methods=['POST'])
def create_gallery():
    # TODO: Data validation
    new_gallery = Galleries(**request.json)
    db.session.add(new_gallery)
    db.session.commit()
    return jsonify(new_gallery.as_dict()), 201

@galleries_bp.route('/galleries/<int:gallery_id>', methods=['GET'])
def get_gallery(gallery_id):
    gallery = Galleries.query.get_or_404(gallery_id)
    return jsonify(gallery.as_dict())

@galleries_bp.route('/galleries/<int:gallery_id>', methods=['PUT'])
def update_gallery(gallery_id):
    gallery = Galleries.query.get_or_404(gallery_id)
    # TODO: Data validation and update
    db.session.commit()
    return jsonify(gallery.as_dict())

@galleries_bp.route('/galleries/<int:gallery_id>', methods=['DELETE'])
def delete_gallery(gallery_id):
    gallery = Galleries.query.get_or_404(gallery_id)
    db.session.delete(gallery)
    db.session.commit()
    return '', 204

# Helper method to serialize the Galleries object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the Galleries class
Galleries.as_dict = as_dict
