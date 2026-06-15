from flask import Blueprint, flash, redirect, url_for, render_template, request, abort
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Collection, Book

bp = Blueprint('collection', __name__, url_prefix='/collections')


@bp.route('/')
@login_required
def index():
    collections = db.session.execute(
        db.select(Collection).where(Collection.user_id == current_user.id)
    ).scalars().all()
    return render_template('collection/index.html', collections=collections)


@bp.route('/<int:collection_id>')
@login_required
def detail(collection_id):
    collection = db.session.execute(
        db.select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not collection:
        flash('Подборка не найдена', 'danger')
        return redirect(url_for('collection.index'))

    return render_template('collection/detail.html', collection=collection)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Название подборки не может быть пустым', 'danger')
        return redirect(url_for('collection.index'))

    try:
        collection = Collection(name=name, user_id=current_user.id)
        db.session.add(collection)
        db.session.commit()
        flash(f'Подборка «{name}» успешно создана', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при создании подборки', 'danger')

    return redirect(url_for('collection.index'))


@bp.route('/add_book', methods=['POST'])
@login_required
def add_book():
    book_id = request.form.get('book_id', type=int)
    collection_id = request.form.get('collection_id', type=int)

    if not book_id or not collection_id:
        flash('Некорректные данные', 'danger')
        return redirect(url_for('main.index'))

    book = db.session.get(Book, book_id)
    if not book:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('main.index'))

    collection = db.session.execute(
        db.select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not collection:
        flash('Подборка не найдена', 'danger')
        return redirect(url_for('book.detail', book_id=book_id))

    if book not in collection.books:
        try:
            collection.books.append(book)
            db.session.commit()
            flash(f'Книга «{book.title}» добавлена в подборку «{collection.name}»', 'success')
        except Exception:
            db.session.rollback()
            flash('Ошибка при добавлении книги в подборку', 'danger')
    else:
        flash('Книга уже есть в этой подборке', 'warning')

    return redirect(url_for('book.detail', book_id=book_id))
