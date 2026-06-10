from flask import Flask, render_template, send_from_directory
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from models import db

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

db.init_app(app)
migrate = Migrate(app, db)


@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(err):
    error_msg = ('Возникла ошибка при подключении к базе данных. '
                 'Повторите попытку позже.')
    return f'{error_msg} (Подробнее: {err})', 500
