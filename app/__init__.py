from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload size
        UPLOAD_FOLDER='app/static/uploads'
    )

    from . import routes
    app.register_blueprint(routes.bp)

    return app