from os import environ as env

from flask import Flask
from mongoengine import connect


def create_app():
    app = Flask(__name__)

    app.config['DB'] = connect(
        db=env.get('DB_NAME'),
        username=env.get('DB_USERNAME'),
        password=env.get('DB_PASSWORD'),
        host=env.get('DB_HOST'),
    )

    app.config['ADDRESS_VERIFY_METHOD'] = env.get('ADDRESS_VERIFY_METHOD', 'sochain')

    from api.escrow import escrow
    app.register_blueprint(escrow)

    return app
