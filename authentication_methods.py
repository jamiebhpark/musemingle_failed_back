from flask import Blueprint, request, jsonify
from musemingle import db

authentication_methods_bp = Blueprint('authentication_methods', __name__)

class AuthenticationMethods(db.Model):
    __tablename__ = 'authentication_methods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    method = db.Column(db.Enum('facebook', 'google', 'apple', 'email'), nullable=False)
    details = db.Column(db.String(255))

@authentication_methods_bp.route('/auth-methods', methods=['GET'])
def get_authentication_methods():
    methods = AuthenticationMethods.query.all()
    return jsonify([method.as_dict() for method in methods])

@authentication_methods_bp.route('/auth-methods', methods=['POST'])
def create_authentication_method():
    # TODO: Data validation
    new_method = AuthenticationMethods(**request.json)
    db.session.add(new_method)
    db.session.commit()
    return jsonify(new_method.as_dict()), 201

@authentication_methods_bp.route('/auth-methods/<int:method_id>', methods=['DELETE'])
def delete_authentication_method(method_id):
    method = AuthenticationMethods.query.get_or_404(method_id)
    db.session.delete(method)
    db.session.commit()
    return '', 204

# Helper method to serialize the AuthenticationMethods object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the AuthenticationMethods class
AuthenticationMethods.as_dict = as_dict
