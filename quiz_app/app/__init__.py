from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main, quiz, auth, settings
    app.register_blueprint(main.bp)
    app.register_blueprint(quiz.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(settings.bp)

    return app
