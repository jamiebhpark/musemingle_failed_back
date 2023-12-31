from flask import Blueprint, request, jsonify, current_app, g
import jwt
import requests
import json
import base64
import os
from users import Users
from authentication_methods import AuthenticationMethods
from musemingle import db
from subscriptions import Subscriptions
from jwt.algorithms import RSAAlgorithm

apple_auth_bp = Blueprint('apple_auth', __name__)

@apple_auth_bp.route('/auth/apple', methods=['POST'])
def authenticate_apple():
    current_app.logger.info(request.json) #로그로 출력

    try:
        token = request.json.get('id_token')
        if not token:
            return jsonify(status="failure", error="id_token is required"), 400

        apple_keys_url = 'https://appleid.apple.com/auth/keys'
        response = requests.get(apple_keys_url)
        response.raise_for_status()
        apple_public_keys = response.json()['keys']

        # 토큰의 헤더를 수동으로 파싱합니다.
        header_data = token.split('.')[0]
        header_data += '=' * (-len(header_data) % 4)  # 패딩 추가
        header = json.loads(base64.b64decode(header_data))

        apple_key = next((k for k in apple_public_keys if k['kid'] == header['kid']), None)
        if not apple_key:
            return jsonify(error="Invalid token header"), 400

        public_key = RSAAlgorithm.from_jwk(json.dumps(apple_key))
        audience = current_app.config.get('APPLE_AUDIENCE', 'manager.musemingle')
        decoded_token = jwt.decode(token, public_key, algorithms=['RS256'], audience=audience)

        user_sub = decoded_token['sub']
        user = Users.query.filter_by(apple_sub=user_sub).first()  # Changed from email to apple_sub
        print(decoded_token)

        subscription = Subscriptions.query.filter_by(role='artist', subscription_type='free').first()
        if subscription is None:
            subscription = Subscriptions(role='artist', subscription_type='free', price=0)
            db.session.add(subscription)
            db.session.commit()

        if not user:
            new_user = Users(email=decoded_token['email'], apple_sub=user_sub, role='artist', subscription_id=subscription.id)
            db.session.add(new_user)
            db.session.commit()
            user = new_user

        auth_method = AuthenticationMethods.query.filter_by(user_id=user.id, method='apple').first()

        if not auth_method:
            new_auth_method = AuthenticationMethods(user_id=user.id, method='apple', details=user_sub)  # Changed from decoded_token['sub'] to user_sub
            db.session.add(new_auth_method)
            db.session.commit()


        return jsonify(status="success", message="Successfully authenticated with Apple"), 200

    except jwt.ExpiredSignatureError:
        return jsonify(status="failure", error="Token has expired"), 401
    except jwt.InvalidTokenError as e:
        current_app.logger.error(f"Invalid token: {str(e)}")
        return jsonify(status="failure", error=f"Invalid token: {str(e)}"), 401
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify(status="failure", error=str(e)), 400


@apple_auth_bp.route('/apple/notifications', methods=['POST'])
def apple_notifications():
    # TODO: You can access the authenticated user here with `g.user`
    try:
        # TODO: Process Apple's server-to-server notifications (e.g., account deletion, email changes, etc.)
        return jsonify(success=True), 200
    except Exception as e:
        return jsonify(error=str(e)), 400
