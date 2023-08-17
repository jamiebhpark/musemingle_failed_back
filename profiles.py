from flask import Blueprint, request, jsonify, send_file
from musemingle import db
from werkzeug.utils import secure_filename
from s3_manager import s3
import os

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

@profiles_bp.route('/profiles/<int:user_id>/profile_image', methods=['GET'])
def get_profile_image(user_id):
    profile = Profiles.query.get_or_404(user_id)
    profile_image_key = profile.profile_image
    file_obj = s3.get_object(Bucket='musemingle-app-images', Key=profile_image_key)
    return send_file(file_obj['Body'], mimetype='image/jpeg')

@profiles_bp.route('/profiles', methods=['POST'])
def create_profile():
    profile_image = request.files['profile_image']
    filename = secure_filename(profile_image.filename)
    profile_image_path = os.path.join('profiles/', filename)
    s3.upload_fileobj(profile_image, 'musemingle-app-images', profile_image_path)

    profile_data = request.json
    profile_data['profile_image'] = profile_image_path
    new_profile = Profiles(**profile_data)
    db.session.add(new_profile)
    db.session.commit()
    return jsonify(new_profile.as_dict()), 201

@profiles_bp.route('/profiles/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    profile = Profiles.query.get_or_404(user_id)
    data = request.json

    for key, value in data.items():
        setattr(profile, key, value)

    profile_image = request.files.get('profile_image')
    if profile_image:
        filename = secure_filename(profile_image.filename)
        profile_image_path = os.path.join('profiles/', filename)
        s3.upload_fileobj(profile_image, 'musemingle-app-images', profile_image_path)
        profile.profile_image = profile_image_path

    db.session.commit()
    return jsonify(profile.as_dict())

@profiles_bp.route('/profiles/<int:user_id>', methods=['DELETE'])
def delete_profile(user_id):
    profile = Profiles.query.get_or_404(user_id)
    profile_image_key = profile.profile_image
    s3.delete_object(Bucket='musemingle-app-images', Key=profile_image_key)

    db.session.delete(profile)
    db.session.commit()
    return '', 204

def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Profiles.as_dict = as_dict
