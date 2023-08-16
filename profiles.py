from flask import Blueprint, request, jsonify
from musemingle import db

profiles_bp = Blueprint('profiles', __name__)

class Profiles(db.Model):
    __tablename__ = 'Profiles'
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True) 
    credentials = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


@profiles_bp.route('/profiles', methods=['GET'])
def get_profiles():
    profiles = Profiles.query.all()
    return jsonify([profile.as_dict() for profile in profiles])

@profiles_bp.route('/profiles', methods=['POST'])
def create_profile():
    new_profile = Profiles(**request.json)
    db.session.add(new_profile)
    db.session.commit()
    return jsonify(new_profile.as_dict()), 201

@profiles_bp.route('/profiles/<int:profile_id>', methods=['PUT'])
def update_profile(profile_id):
    profile = Profiles.query.get_or_404(profile_id)
    db.session.commit()
    return jsonify(profile.as_dict())

@profiles_bp.route('/profiles/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    profile = Profiles.query.get_or_404(profile_id)
    db.session.delete(profile)
    db.session.commit()
    return '', 204

# Helper method to serialize the Profiles object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the Profiles class
Profiles.as_dict = as_dict
