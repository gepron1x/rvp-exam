from flask import Blueprint, render_template, request

from app import db
from app.models import Book

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    pagination = db.paginate(
        db.select(Book).order_by(Book.year.desc()),
        page=page,
        per_page=per_page,
        error_out=False
    )

    books = pagination.items
    return render_template('index.html',
                           books=books,
                           pagination=pagination)