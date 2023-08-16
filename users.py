from flask import Blueprint, jsonify, request
from musemingle import db

users_bp = Blueprint('users', __name__)

class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.Enum('artist', 'gallery'), nullable=False)
    subscription_type = db.Column(db.Enum('free', 'premium'), nullable=False)
    subscription_fee_id = db.Column(db.Integer, db.ForeignKey('SubscriptionFees.id'))
    password_hash = db.Column(db.String(255))
    password_salt = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

@users_bp.route('/users', methods=['GET'])
def get_users():
    users = Users.query.all()
    return jsonify([user.as_dict() for user in users])

@users_bp.route('/users', methods=['POST'])
def create_user():
    # TODO: Data validation
    new_user = Users(**request.json)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.as_dict()), 201

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = Users.query.get_or_404(user_id)
    return jsonify(user.as_dict())

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = Users.query.get_or_404(user_id)
    # TODO: Data validation and update
    db.session.commit()
    return jsonify(user.as_dict())

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

# Helper method to serialize the User object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the Users class
Users.as_dict = as_dict
