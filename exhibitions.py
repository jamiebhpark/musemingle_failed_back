from flask import Blueprint, jsonify, request, send_file
from musemingle import db
from werkzeug.utils import secure_filename
from s3_manager import s3
import os

exhibitions_bp = Blueprint('exhibitions', __name__)

class Exhibitions(db.Model):
    __tablename__ = 'exhibitions'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gallery_id = db.Column(db.Integer, db.ForeignKey('galleries.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('upcoming', 'ongoing', 'ended'))
    poster_image = db.Column(db.String(255)) # S3 key for the poster image
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

@exhibitions_bp.route('/exhibitions', methods=['GET'])
def get_exhibitions():
    exhibitions = Exhibitions.query.all()
    return jsonify([exhibition.as_dict() for exhibition in exhibitions])

@exhibitions_bp.route('/exhibitions/<int:exhibition_id>/poster_image', methods=['GET'])
def get_poster_image(exhibition_id):
    exhibition = Exhibitions.query.get_or_404(exhibition_id)
    poster_image_key = exhibition.poster_image

    # Download poster image from S3
    file_obj = s3.get_object(Bucket='musemingle-app-images', Key=f'exhibitions/{poster_image_key}')
    return send_file(file_obj['Body'], mimetype='image/jpeg')

@exhibitions_bp.route('/exhibitions', methods=['POST'])
def create_exhibition():
    data = request.json
    exhibition = Exhibitions(**data)
    db.session.add(exhibition)
    db.session.commit()

    # Assuming the poster image is sent as a file
    poster_image = request.files['poster_image']
    if poster_image:
        filename = secure_filename(poster_image.filename)
        s3.put_object(Bucket='musemingle-app-images', Key=f'exhibitions/{filename}', Body=poster_image)
        exhibition.poster_image = filename
        db.session.commit()

    return jsonify(exhibition.as_dict()), 201

@exhibitions_bp.route('/exhibitions/<int:exhibition_id>', methods=['PUT'])
def update_exhibition(exhibition_id):
    exhibition = Exhibitions.query.get_or_404(exhibition_id)
    data = request.json
    for key, value in data.items():
        setattr(exhibition, key, value)

    poster_image = request.files.get('poster_image')
    if poster_image:
        filename = secure_filename(poster_image.filename)
        s3.put_object(Bucket='musemingle-app-images', Key=f'exhibitions/{filename}', Body=poster_image)
        exhibition.poster_image = filename

    db.session.commit()
    return jsonify(exhibition.as_dict())

@exhibitions_bp.route('/exhibitions/<int:exhibition_id>', methods=['DELETE'])
def delete_exhibition(exhibition_id):
    exhibition = Exhibitions.query.get_or_404(exhibition_id)
    
    # Deleting the poster image from S3
    if exhibition.poster_image:
        s3.delete_object(Bucket='musemingle-app-images', Key=f'exhibitions/{exhibition.poster_image}')

    db.session.delete(exhibition)
    db.session.commit()
    return '', 204

def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Exhibitions.as_dict = as_dict
