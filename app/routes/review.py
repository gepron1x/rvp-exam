import bleach
from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required, current_user

from app import db
from app.forms.review_form import ReviewForm
from app.models import Book, Review
from app.roles import role_required, MODERATOR

bp = Blueprint('review', __name__)


@bp.route('/book/<int:book_id>/review/create', methods=['GET', 'POST'])
@login_required
def create(book_id: int):
    book = Book.query.get_or_404(book_id)

    stmt_user_review = db.select(Review).where(
        Review.book_id == book_id,
        Review.user_id == current_user.id
    )
    user_review = db.session.execute(stmt_user_review).scalar_one_or_none()
    if user_review:
        flash("Вы уже написали рецензию на эту книгу.", "danger")
        return redirect(url_for('book.detail', book_id=book_id))

    form = ReviewForm()

    if form.validate_on_submit():
        text = form.text.data or ""
        sanitized_text = bleach.clean(text)


        try:
            book.add_review(current_user.id, int(form.rating.data), sanitized_text)
            db.session.commit()
            flash("Рецензия успешно опубликована!", "success")
            return redirect(url_for('book.detail', book_id=book_id))
        except Exception as e:
            db.session.rollback()
            flash("Ошибка при сохранении рецензии.", "danger")

    return render_template('book/review.html', book=book, form=form)

@bp.route('/book/<int:book_id>/review/<int:review_id>/delete', methods=['POST'])
@role_required(MODERATOR)
def delete(book_id: int, review_id: int):
    book = db.get_or_404(Book, book_id)
    review = db.session.execute(
        db.select(Review).where(Review.id == review_id, Review.book_id == book_id)
    ).scalar_one_or_none()

    if not review:
        flash('Рецензия не найдена.', 'danger')
        return redirect(url_for('book.detail', book_id=book_id))

    try:
        book.remove_review(review)
        db.session.commit()
        flash('Рецензия успешно удалена.', 'success')
    except Exception:
        db.session.rollback()
        flash('Ошибка при удалении рецензии.', 'danger')

    return redirect(url_for('book.detail', book_id=book_id))

