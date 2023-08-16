from flask import Blueprint, request, jsonify
from musemingle import db

subscription_fees_bp = Blueprint('subscription_fees', __name__)

class SubscriptionFees(db.Model):
    __tablename__ = 'Subscription_Fees'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role = db.Column(db.Enum('artist', 'gallery'), nullable=False)
    subscription_type = db.Column(db.Enum('free', 'premium'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

@subscription_fees_bp.route('/sub-fees', methods=['GET'])
def get_subscription_fees():
    fees = SubscriptionFees.query.all()
    return jsonify([fee.as_dict() for fee in fees])

@subscription_fees_bp.route('/sub-fees', methods=['POST'])
def create_subscription_fee():
    # TODO: Data validation
    new_fee = SubscriptionFees(**request.json)
    db.session.add(new_fee)
    db.session.commit()
    return jsonify(new_fee.as_dict()), 201

@subscription_fees_bp.route('/sub-fees/<int:fee_id>', methods=['PUT'])
def update_subscription_fee(fee_id):
    fee = SubscriptionFees.query.get_or_404(fee_id)
    # TODO: Data validation and update
    db.session.commit()
    return jsonify(fee.as_dict())

@subscription_fees_bp.route('/sub-fees/<int:fee_id>', methods=['DELETE'])
def delete_subscription_fee(fee_id):
    fee = SubscriptionFees.query.get_or_404(fee_id)
    db.session.delete(fee)
    db.session.commit()
    return '', 204

# Helper method to serialize the SubscriptionFees object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the SubscriptionFees class
SubscriptionFees.as_dict = as_dict
