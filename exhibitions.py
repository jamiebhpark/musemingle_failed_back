from flask import Blueprint, jsonify, request
from musemingle import db

exhibitions_bp = Blueprint('exhibitions', __name__)

class Exhibitions(db.Model):
    __tablename__ = 'Exhibitions'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gallery_id = db.Column(db.Integer, db.ForeignKey('galleries.id'))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('upcoming', 'ongoing', 'ended'))
    poster_image = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

@exhibitions_bp.route('/exhibitions', methods=['GET'])
#@app.route('/exhibitions', methods=['GET'])
def get_exhibitions():
    exhibitions = Exhibitions.query.all()
    return jsonify([exhibition.as_dict() for exhibition in exhibitions])

@exhibitions_bp.route('/exhibitions', methods=['POST'])
#@app.route('/exhibitions', methods=['POST'])
def create_exhibition():
    # TODO: Data validation
    new_exhibition = Exhibitions(**request.json)
    db.session.add(new_exhibition)
    db.session.commit()
    return jsonify(new_exhibition.as_dict()), 201

@exhibitions_bp.route('/exhibitions/<int:exhibition_id>', methods=['GET'])
#@app.route('/exhibitions/<int:exhibition_id>', methods=['GET'])
def get_exhibition(exhibition_id):
    exhibition = Exhibitions.query.get_or_404(exhibition_id)
    return jsonify(exhibition.as_dict())

@exhibitions_bp.route('/exhibitions/<int:exhibition_id>', methods=['PUT'])
#@app.route('/exhibitions/<int:exhibition_id>', methods=['PUT'])
def update_exhibition(exhibition_id):
    exhibition = Exhibitions.query.get_or_404(exhibition_id)
    # TODO: Data validation and update
    db.session.commit()
    return jsonify(exhibition.as_dict())

@exhibitions_bp.route('/exhibitions/<int:exhibition_id>', methods=['DELETE'])
#@app.route('/exhibitions/<int:exhibition_id>', methods=['DELETE'])
def delete_exhibition(exhibition_id):
    exhibition = Exhibitions.query.get_or_404(exhibition_id)
    db.session.delete(exhibition)
    db.session.commit()
    return '', 204

# Helper method to serialize the Exhibitions object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    return {c.name: getattr(self, c.name) for c in self.__table__.columns}
# Add this method to the Exhibitions class
Exhibitions.as_dict = as_dict
