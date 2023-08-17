from flask import Blueprint, request, jsonify
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import requests
from users import Users
from authentication_methods import AuthenticationMethods
from musemingle import db
from jwt.algorithms import RSAAlgorithm

apple_auth_bp = Blueprint('apple_auth', __name__)

@apple_auth_bp.route('/auth/apple', methods=['POST'])
def authenticate_apple():
    try:
        # TODO: Data validation
        token = request.json.get('id_token')

        # Load Apple public keys
        apple_keys_url = 'https://appleid.apple.com/auth/keys'
        apple_public_keys = requests.get(apple_keys_url).json()['keys']

        # Decode and verify the token
        header = jwt.get_unverified_header(token)
        apple_key = [k for k in apple_public_keys if k['kid'] == header['kid']][0]
        public_key = RSAAlgorithm.from_jwk(jwt.json.dumps(apple_key))
        decoded_token = jwt.decode(token, public_key, algorithms=['RS256'], audience='manager.musemingle')

        user_email = decoded_token['email']

        # Check if user already exists in the database
        user = Users.query.filter_by(email=user_email).first()

        if not user:
            # Create new user in the Users table
            new_user = Users(email=user_email, role='artist', subscription_type='free')
            db.session.add(new_user)
            db.session.commit()
            user = new_user

        # Check if the authentication method already exists
        auth_method = AuthenticationMethods.query.filter_by(user_id=user.id, method='apple').first()

        if not auth_method:
            new_auth_method = AuthenticationMethods(user_id=user.id, method='apple', details=decoded_token['sub'])
            db.session.add(new_auth_method)
            db.session.commit()

        return jsonify(user.as_dict()), 200
    except Exception as e:
        return jsonify(error=str(e)), 400

@apple_auth_bp.route('/apple/notifications', methods=['POST'])
def apple_notifications():
    try:
        # TODO: Process Apple's server-to-server notifications (e.g., account deletion, email changes, etc.)
        return jsonify(success=True), 200
    except Exception as e:
        return jsonify(error=str(e)), 400
