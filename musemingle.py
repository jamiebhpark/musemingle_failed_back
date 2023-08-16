# musemingle.py

from flask import Flask
from database import db, init_db

def create_app():
    app = Flask(__name__)
    init_db(app)

    from exhibitions import exhibitions_bp
    app.register_blueprint(exhibitions_bp)

    from artworks import artworks_bp
    app.register_blueprint(artworks_bp)

    from categories import categories_bp
    app.register_blueprint(categories_bp)

    from profiles import profiles_bp
    app.register_blueprint(profiles_bp)

    from users import users_bp
    app.register_blueprint(users_bp)

    from artwork_categories import artwork_categories_bp
    app.register_blueprint(artwork_categories_bp)

    from authentication_methods import authentication_methods_bp
    app.register_blueprint(authentication_methods_bp)

    from galleries import galleries_bp
    app.register_blueprint(galleries_bp)

    from subscription_fees import subscription_fees_bp
    app.register_blueprint(subscription_fees_bp)

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
