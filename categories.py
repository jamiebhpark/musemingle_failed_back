from flask import Blueprint, request, jsonify
from musemingle import db

categories_bp = Blueprint('categories', __name__)

class Categories(db.Model):
    __tablename__ = 'Categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Categories.query.all()
    return jsonify([category.as_dict() for category in categories])

@categories_bp.route('/categories', methods=['POST'])
def create_category():
    new_category = Categories(**request.json)
    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.as_dict()), 201

@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Categories.query.get_or_404(category_id)
    db.session.commit()
    return jsonify(category.as_dict())

@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Categories.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return '', 204

# Helper method to serialize the Categories object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the Categories class
Categories.as_dict = as_dict
