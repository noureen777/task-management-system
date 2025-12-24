from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    import os
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(os.path.dirname(base_dir), 'templates')
    static_dir = os.path.join(os.path.dirname(base_dir), 'static')

    app = Flask(__name__,
                template_folder=template_dir,
                static_folder=static_dir)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'

    db.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app