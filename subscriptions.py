from flask import Blueprint, request, jsonify
from musemingle import db

subscriptions_bp = Blueprint('subscriptions', __name__)

class Subscriptions(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role = db.Column(db.Enum('artist', 'gallery'), nullable=False)
    subscription_type = db.Column(db.Enum('free', 'premium'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

@subscriptions_bp.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    subscriptions = Subscriptions.query.all()
    return jsonify([subscription.as_dict() for subscription in subscriptions])

@subscriptions_bp.route('/subscriptions', methods=['POST'])
def create_subscription():
    # TODO: Data validation
    new_subscription = Subscriptions(**request.json)
    db.session.add(new_subscription)
    db.session.commit()
    return jsonify(new_subscription.as_dict()), 201

@subscriptions_bp.route('/subscriptions/<int:subscription_id>', methods=['PUT'])
def update_subscription(subscription_id):
    subscription = Subscriptions.query.get_or_404(subscription_id)
    # TODO: Data validation and update
    db.session.commit()
    return jsonify(subscription.as_dict())

@subscriptions_bp.route('/subscriptions/<int:subscription_id>', methods=['DELETE'])
def delete_subscription(subscription_id):
    subscription = Subscriptions.query.get_or_404(subscription_id)
    db.session.delete(subscription)
    db.session.commit()
    return '', 204

# Helper method to serialize the Subscriptions object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the Subscriptions class
Subscriptions.as_dict = as_dict
