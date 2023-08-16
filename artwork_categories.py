from flask import Blueprint, request, jsonify
from musemingle import db

artwork_categories_bp = Blueprint('artwork_categories', __name__)

class ArtworkCategories(db.Model):
    __tablename__ = 'ArtworkCategories'
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)
    added_date = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP')) # 추가된 필드

@artwork_categories_bp.route('/art-categories', methods=['GET'])
def get_artwork_categories():
    categories = ArtworkCategories.query.all()
    return jsonify([category.as_dict() for category in categories])

@artwork_categories_bp.route('/art-categories', methods=['POST'])
def create_artwork_category():
    # TODO: Data validation
    new_category = ArtworkCategories(**request.json)
    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.as_dict()), 201

@artwork_categories_bp.route('/art-categories/<int:artwork_id>/<int:category_id>', methods=['DELETE'])
def delete_artwork_category(artwork_id, category_id):
    category = ArtworkCategories.query.filter_by(artwork_id=artwork_id, category_id=category_id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    return '', 204

# Helper method to serialize the ArtworkCategories object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the ArtworkCategories class
ArtworkCategories.as_dict = as_dict
