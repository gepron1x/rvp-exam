from flask import Blueprint, render_template

from app import db
from app.models import Book

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    books = db.session.execute(
        db.select(Book).order_by(Book.year.desc())
    ).scalars().all()
    return render_template('index.html', books=books)