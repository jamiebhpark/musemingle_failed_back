from flask import Blueprint, request, jsonify
import requests
from users import Users
from authentication_methods import AuthenticationMethods
from musemingle import db

facebook_auth_bp = Blueprint('facebook_auth', __name__)

@facebook_auth_bp.route('/auth/facebook', methods=['POST'])
def authenticate_facebook():
    try:
        # TODO: Data validation
        access_token = request.json.get('access_token')
        facebook_app_id = "3339811726329949"
        facebook_app_secret = "56996353ec12eceb7b8774fe12e50274"

        # Verify token
        debug_token_url = f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={facebook_app_id}|{facebook_app_secret}"
        response = requests.get(debug_token_url).json()

        if 'error' in response:
            raise ValueError('Invalid token')

        user_id = response['data']['user_id']

        # Get user information
        user_info_url = f"https://graph.facebook.com/{user_id}?fields=id,name,email&access_token={access_token}"
        user_info = requests.get(user_info_url).json()
        
        user_email = user_info['email']

        # Check if user already exists in the database
        user = Users.query.filter_by(email=user_email).first()

        if not user:
            # Create new user in the Users table
            new_user = Users(email=user_email, username=user_info['name'], role='artist', subscription_type='free')
            db.session.add(new_user)
            db.session.commit()
            user = new_user

        # Check if the authentication method already exists
        auth_method = AuthenticationMethods.query.filter_by(user_id=user.id, method='facebook').first()

        if not auth_method:
            new_auth_method = AuthenticationMethods(user_id=user.id, method='facebook', details=user_info['id'])
            db.session.add(new_auth_method)
            db.session.commit()

        return jsonify(user.as_dict()), 200
    except Exception as e:
        return jsonify(error=str(e)), 400
