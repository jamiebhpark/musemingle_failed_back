from flask import Blueprint, jsonify, request, session
from musemingle import db
from subscriptions import Subscriptions

users_bp = Blueprint('users', __name__)

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.Enum('artist', 'gallery'), nullable=False)
    apple_sub = db.Column(db.String(255), unique=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'))
    auth_method_id = db.Column(db.Integer, db.ForeignKey('authentication_methods.id'))
    password_hash = db.Column(db.String(255))
    password_salt = db.Column(db.String(255))
    credentials = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    degree_certificate = db.Column(db.String(255))
    portfolio = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean)
    created_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP'))
    updated_at = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

@users_bp.route('/users', methods=['GET'])
def get_users():
    users = Users.query.all()
    return jsonify([user.as_dict() for user in users])

@users_bp.route('/users', methods=['POST'])
def create_user():
    # TODO: Data validation
    apple_sub = request.json.get('apple_sub', None)
    if apple_sub:
        request.json['apple_sub'] = apple_sub  # 애플 로그인으로부터 받은 'sub' 값을 저장
    subscription_type = request.json.get('subscription_type')
    subscription = Subscriptions.query.filter_by(subscription_type=subscription_type).first()
    if subscription:
        request.json['subscription_id'] = subscription.id
        del request.json['subscription_type']

    new_user = Users(**request.json)
    db.session.add(new_user)

    for image_field in ['profile_image', 'degree_certificate', 'portfolio']:
        image_file = request.files.get(image_field)
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join('users/', filename)
            s3.upload_fileobj(image_file, 'musemingle-app-images', image_path)
            setattr(new_user, image_field, image_path)

    db.session.commit()
    return jsonify(new_user.as_dict()), 201

#@users_bp.route('/users/<int:user_id>', methods=['GET'])
#def get_user(user_id):
 #   user = Users.query.get_or_404(user_id)
  #  return jsonify(user.as_dict())
#@users_bp.route('/current_user', methods=['GET'])
#def get_current_user():
    # TODO: 사용자를 식별하는 로직 (예: 토큰/세션 검증)
   # user_id = "CURRENT_LOGGED_IN_USER_ID"
   # user = Users.query.get(user_id)
   # return jsonify(user.as_dict())

@users_bp.route('/current_user', methods=['GET'])
def get_current_user():
    # 로그인 로직에 따라 session에서 user_id를 가져옵니다.
    user_id = session.get('user_id', None)

    if not user_id:
        return jsonify({"error": "No user logged in"}), 401

    user = Users.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.as_dict())



@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = Users.query.get_or_404(user_id)

    for image_field in ['profile_image', 'degree_certificate', 'portfolio']:
        image_file = request.files.get(image_field)
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join('users/', filename)
            s3.put_object(Bucket='musemingle-app-images', Key=image_path, Body=image_file)
            setattr(user, image_field, image_path)

    # TODO: Data validation and update
    db.session.commit()
    return jsonify(user.as_dict())

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)

    for image_field in ['profile_image', 'degree_certificate', 'portfolio']:
        image_key = getattr(user, image_field)
        if image_key:
            s3.delete_object(Bucket='musemingle-app-images', Key=image_key)

    db.session.delete(user)
    db.session.commit()
    return '', 204

@users_bp.route('/users/logout', methods=['POST'])
def logout():
    # 세션에서 user_id 제거
    if 'user_id' in session:
        session.pop('user_id')
    # (추가적인 토큰 무효화 로직이 필요한 경우 여기에 추가)
    
    return jsonify({"message": "Successfully logged out"}), 200

# Helper method to serialize the User object
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Add this method to the Users class
Users.as_dict = as_dict
