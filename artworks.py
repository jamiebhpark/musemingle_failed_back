from flask import Blueprint, request, jsonify
from musemingle import db
from werkzeug.utils import secure_filename
import os
from s3_manager import s3

artworks_bp = Blueprint('artworks', __name__)

class Artworks(db.Model):
    __tablename__ = 'artworks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    creation_date = db.Column(db.Date, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    category_name = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

@artworks_bp.route('/artworks', methods=['GET'])
def get_artworks():
    artworks = Artworks.query.all()
    return jsonify([artwork.as_dict() for artwork in artworks])

@artworks_bp.route('/artworks/<int:artwork_id>/image', methods=['GET'])
def get_image(artwork_id):
    artwork = Artworks.query.get_or_404(artwork_id)
    image_key = artwork.image

    # Download image from S3
    file_obj = s3.get_object(Bucket='musemingle-app-images', Key=image_key)
    return send_file(file_obj['Body'], mimetype='image/jpeg')

@artworks_bp.route('/artworks', methods=['POST'])
def create_artwork():
    image_file = request.files['image']
    filename = secure_filename(image_file.filename)
    image_path = os.path.join('artworks/', filename)

    # Upload image to S3
    s3.upload_fileobj(image_file, 'musemingle-app-images', image_path)

    # Save image key to database
    artwork_data = request.json
    artwork_data['image_key'] = image_path
    new_artwork = Artworks(**artwork_data)
    db.session.add(new_artwork)
    db.session.commit()
    return jsonify(new_artwork.as_dict()), 201

@artworks_bp.route('/artworks/<int:artwork_id>', methods=['PUT'])
def update_artwork(artwork_id):
    artwork = Artworks.query.get_or_404(artwork_id)
    for key, value in request.json.items():
        setattr(artwork, key, value)
    if 'image' in request.files:
        image_file = request.files['image']
        filename = secure_filename(image_file.filename)
        image_path = os.path.join('artworks/', filename)
        s3.upload_fileobj(image_file, 'musemingle-app-images', image_path)
        artwork.image_key = image_path
    db.session.commit()
    return jsonify(artwork.as_dict())

@artworks_bp.route('/artworks/<int:artwork_id>', methods=['DELETE'])
def delete_artwork(artwork_id):
    artwork = Artworks.query.get_or_404(artwork_id)
    image_key = artwork.image_key

    # Delete image from S3
    s3.delete_object(Bucket='musemingle-app-images', Key=image_key)

    # Delete artwork from database
    db.session.delete(artwork)
    db.session.commit()
    return '', 204

# Helper method to serialize the Artworks object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the Artworks class
Artworks.as_dict = as_dict
