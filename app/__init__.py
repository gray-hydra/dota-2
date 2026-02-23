import logging
import os
from flask import Flask

def create_app() -> Flask:
    app = Flask(__name__)

    # Logging setup - only our app, not Werkzeug
    os.makedirs('logs', exist_ok=True)  # create folder if missing
    # handler = logging.FileHandler('logs/app.log')  # write to file
    # handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))  # timestamp + level
    # app.logger.addHandler(handler)  # attach to Flask
    # app.logger.setLevel(logging.INFO)  # minimum log level

    # TEMPORARY: verbose logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    app.logger.setLevel(logging.DEBUG)

    from app.routes import main
    app.register_blueprint(main)

    return app
