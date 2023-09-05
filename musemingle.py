# musemingle.py

from flask import Flask
from database import db, init_db
from flask_migrate import Migrate
#import logging

def create_app():
    app = Flask(__name__)
   # logging.basicConfig(filename='error.log', level=logging.DEBUG)
    init_db(app)

    from exhibitions import exhibitions_bp
    app.register_blueprint(exhibitions_bp)

    from artworks import artworks_bp
    app.register_blueprint(artworks_bp)

    from users import users_bp
    app.register_blueprint(users_bp)

    from authentication_methods import authentication_methods_bp
    app.register_blueprint(authentication_methods_bp)

    from galleries import galleries_bp
    app.register_blueprint(galleries_bp)

    from subscriptions import subscriptions_bp
    app.register_blueprint(subscriptions_bp)

    from s3_manager import s3_manager_bp
    app.register_blueprint(s3_manager_bp)

    from google_auth import google_auth_bp
    app.register_blueprint(google_auth_bp)

    from apple_auth import apple_auth_bp
    app.register_blueprint(apple_auth_bp)

    from facebook_auth import facebook_auth_bp
    app.register_blueprint(facebook_auth_bp)

    migrate = Migrate(app, db)

    @app.route('/')
    def hello_world():
        return 'Hello, World!'

    @app.route('/urls')
    def urls():
        return '<br>'.join(str(rule) for rule in app.url_map.iter_rules())

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', debug=True)
