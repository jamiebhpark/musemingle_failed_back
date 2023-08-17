from flask import Blueprint, request, jsonify
from musemingle import db
from users import Users
from authentication_methods import AuthenticationMethods
from oauth2client.client import verify_id_token
from oauth2client.crypt import AppIdentityError

google_auth_bp = Blueprint('google_auth', __name__)

@google_auth_bp.route('/auth/google', methods=['POST'])
def authenticate_google():
    try:
        # TODO: Data validation
        token = request.json.get('id_token')
        google_client_id = "685256007772-j7di2r0d2qaja76nk4n8iede2t7r5q4s.apps.googleusercontent.com"

        # Verify token
        id_info = verify_id_token(token, google_client_id)

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        user_email = id_info['email']

        # Check if user already exists in the database
        user = Users.query.filter_by(email=user_email).first()

        if not user:
            # Create new user in the Users table
            new_user = Users(email=user_email, username=id_info['name'], role='artist', subscription_type='free')
            db.session.add(new_user)
            db.session.commit()
            user = new_user

        # Add or update the authentication method
        auth_method = AuthenticationMethods.query.filter_by(user_id=user.id, method='google').first()

        if not auth_method:
            new_auth_method = AuthenticationMethods(user_id=user.id, method='google', details=id_info['sub'])
            db.session.add(new_auth_method)
            db.session.commit()
        else:
            # Update auth method details if needed
            pass

        return jsonify(user.as_dict()), 200

    except AppIdentityError:
        return jsonify(error='Invalid token'), 401
    except Exception as e:
        return jsonify(error=str(e)), 400

