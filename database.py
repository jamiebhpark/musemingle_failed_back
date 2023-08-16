from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://jamie:903ehgk903!@musemingledb.cebfspm81gip.ap-northeast-2.rds.amazonaws.com:3306/musemingledb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

