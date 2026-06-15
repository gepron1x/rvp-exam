import hashlib
import os

import bleach
import markdown
from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import current_user
from sqlalchemy import select

from app.extensions import db
from app.forms.book_form import BookForm
from app.models import Book, Genre, Review, Collection
from app.cover_upload import create_cover, save_cover, delete_cover, delete_file
from app.roles import role_required
from app.roles import ADMIN, MODERATOR

bp = Blueprint('book', __name__, url_prefix='/book')


def clean_text(description: str):
    return bleach.clean(description)

@bp.route('/create', methods=['GET', 'POST'])
@role_required(ADMIN)
def create():
    form = BookForm()

    if form.validate_on_submit():
        try:
            file = form.cover.data
            cover = create_cover(file)

            book = Book(
                title=form.title.data,
                description=clean_text(form.description.data),
                year=form.year.data,
                publisher=form.publisher.data,
                pages=form.pages.data,
                cover_id=cover.id,
                rating_sum=0,
                rating_num=0
            )

            db.session.add(book)
            db.session.flush()

            stmt = db.select(Genre).where(Genre.id.in_(form.genres.data))
            genres = db.session.execute(stmt).scalars().all()
            book.genres = genres

            db.session.commit()
            save_cover(cover, file) # Сохраняем файл после успешного добавления в БД
            flash('Книга успешно добавлена!', 'success')
            return redirect(url_for('book.detail', book_id=book.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении книги: {str(e)}', 'danger')
            raise e
    genres = db.session.execute(db.select(Genre)).scalars().all()
    return render_template('book/create.html', form=form, genres=genres)


@bp.route('/<int:book_id>')
def detail(book_id: int):
    stmt = db.select(Book).where(Book.id == book_id)
    book = db.session.execute(stmt).scalar_one_or_none()

    if not book:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('main.index'))

    stmt_reviews = db.select(Review).where(Review.book_id == book_id).order_by(Review.created_at.desc())
    reviews = db.session.execute(stmt_reviews).scalars().all()

    user_review = None
    user_can_review = False
    user_collections = []

    if current_user.is_authenticated:
        stmt_user_review = db.select(Review).where(
            Review.book_id == book_id,
            Review.user_id == current_user.id
        )
        user_review = db.session.execute(stmt_user_review).scalar_one_or_none()
        user_can_review = user_review is None

        user_collections = db.session.execute(
            db.select(Collection).where(Collection.user_id == current_user.id)
        ).scalars().all()

    book_description_html = markdown.markdown(book.description)

    return render_template('book/book.html',
                           book=book,
                           reviews=reviews,
                           user_review=user_review,
                           user_can_review=user_can_review,
                           book_description_html=book_description_html,
                           user_collections=user_collections)

@bp.route("/<int:book_id>/edit", methods=['GET', 'POST'])
@role_required(MODERATOR)
def edit(book_id: int):
    stmt = db.select(Book).where(Book.id == book_id)
    book = db.session.execute(stmt).scalar_one_or_none()

    if not book:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('main.index'))

    form = BookForm()

    if form.validate_on_submit():
        try:
            book.title = form.title.data
            book.description = clean_text(form.description.data)
            book.year = form.year.data
            book.publisher = form.publisher.data
            book.pages = form.pages.data

            stmt = db.select(Genre).where(Genre.id.in_(form.genres.data))
            genres = db.session.execute(stmt).scalars().all()
            book.genres = genres

            db.session.commit()
            flash('Книга успешно обновлена!', 'success')
            return redirect(url_for('book.detail', book_id=book.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении книги: {str(e)}', 'danger')
    elif request.method == 'GET':
        form.title.data = book.title
        form.description.data = book.description
        form.year.data = book.year
        form.publisher.data = book.publisher
        form.pages.data = book.pages
        form.genres.data = [g.id for g in book.genres]
    genres = db.session.execute(db.select(Genre)).scalars().all()
    return render_template('book/edit.html', form=form, book=book, genres=genres)

@bp.route("/<int:book_id>/delete", methods=['POST'])
@role_required(ADMIN)
def delete(book_id: int):
    stmt = db.select(Book).where(Book.id == book_id)
    book = db.session.execute(stmt).scalar_one_or_none()

    if not book:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('main.index'))

    try:
        db.session.delete(book)
        db.session.flush()
        cover = book.cover
        should_delete_file = delete_cover(cover)
        db.session.commit()
        if should_delete_file:
            delete_file(cover)
        flash("Книга успешно удалена", "success")
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении книги: {e}', 'danger')
        return redirect(url_for('main.index'))



