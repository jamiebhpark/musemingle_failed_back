from flask import Blueprint, request, jsonify
from musemingle import db

galleries_bp = Blueprint('galleries', __name__)

class Galleries(db.Model):
    __tablename__ = 'galleries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    country = db.Column(db.String(255))
    zip_code = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean)
    website = db.Column(db.String(255))
    verification_document = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

@galleries_bp.route('/galleries', methods=['GET'])
def get_galleries():
    galleries = Galleries.query.all()
    return jsonify([gallery.as_dict() for gallery in galleries])

@galleries_bp.route('/galleries', methods=['POST'])
def create_gallery():
    # TODO: Data validation
    new_gallery = Galleries(**data)
    db.session.add(new_gallery)
    db.session.commit()

    verification_document_file = request.files.get('verification_document')
    if verification_document_file:
        filename = secure_filename(verification_document_file.filename)
        document_path = os.path.join('galleries/', filename)
        s3.upload_fileobj(verification_document_file, 'musemingle-app-images', document_path)
        new_gallery.verification_document = document_path
        db.session.commit()

    return jsonify(new_gallery.as_dict()), 201

@galleries_bp.route('/galleries/<int:gallery_id>', methods=['GET'])
def get_gallery(gallery_id):
    gallery = Galleries.query.get_or_404(gallery_id)
    return jsonify(gallery.as_dict())

@galleries_bp.route('/galleries/<int:gallery_id>', methods=['PUT'])
def update_gallery(gallery_id):

    gallery = Galleries.query.get_or_404(gallery_id)
    data = request.json
    for key, value in data.items():
        setattr(gallery, key, value)

    verification_document_file = request.files.get('verification_document')
    if verification_document_file:
        filename = secure_filename(verification_document_file.filename)
        document_path = os.path.join('galleries/', filename)
        s3.put_object(Bucket='musemingle-app-images', Key=document_path, Body=verification_document_file)
        gallery.verification_document = document_path

    db.session.commit()
    return jsonify(gallery.as_dict())

@galleries_bp.route('/galleries/<int:gallery_id>', methods=['DELETE'])
def delete_gallery(gallery_id):
    gallery = Galleries.query.get_or_404(gallery_id)

    document_key = gallery.verification_document
    if document_key:
        s3.delete_object(Bucket='musemingle-app-images', Key=document_key)

    db.session.delete(gallery)
    db.session.commit()
    return '', 204

# Helper method to serialize the Galleries object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the Galleries class
Galleries.as_dict = as_dict
