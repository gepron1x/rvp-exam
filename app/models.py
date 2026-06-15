import os
from typing import Optional, List
from datetime import datetime

import markdown
from flask import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Integer, Table, Column

from .extensions import db
class Role(db.Model):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    role: Mapped["Role"] = relationship()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    def __repr__(self):
        return '<User %r>' % self.login

book_genre = Table(
    'book_genre',
    db.Model.metadata,
    Column('book_id', Integer, ForeignKey('books.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)
)


class Genre(db.Model):
    __tablename__ = 'genres'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)

    books: Mapped[List["Book"]] = relationship(
        secondary=book_genre,
        back_populates="genres",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Genre(name={self.name})>"

class Cover(db.Model):
    __tablename__ = 'covers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime: Mapped[str] = mapped_column(String(100), nullable=False)
    md5_hash: Mapped[str] = mapped_column(String(100), nullable=False)

    @property
    def url(self):
        return url_for('static', filename=os.path.join(f'upload/covers/{self.file_name}'))

class Book(db.Model):
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    publisher: Mapped[str] = mapped_column(String(100), nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    cover_id: Mapped[int] = mapped_column(ForeignKey("covers.id"))

    rating_sum: Mapped[int] = mapped_column(default=0)
    rating_num: Mapped[int] = mapped_column(default=0)

    cover: Mapped["Cover"] = relationship()

    genres: Mapped[List["Genre"]] = relationship(
        secondary=book_genre,
        back_populates="books",
        lazy="selectin"
    )

    reviews: Mapped[List["Review"]] = relationship(
        "Review",
        back_populates="book",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def add_review(self, user_id: int, rating: int, text: str = ""):

        stmt = db.select(Review).where(
            Review.book_id == self.id,
            Review.user_id == user_id
        )
        existing_review = db.session.execute(stmt).scalar_one_or_none()

        if existing_review:
            raise ValueError("Пользователь уже оставил отзыв на эту книгу")

        review = Review(
            book_id=self.id,
            user_id=user_id,
            rating=rating,
            text=text
        )

        self.rating_sum += rating
        self.rating_num += 1
        db.session.add(review)
        db.session.flush()

        return review

    def remove_review(self, review: "Review"):
        if review.book_id != self.id:
            raise ValueError("Отзыв не принадлежит этой книге")

        self.rating_sum -= review.rating
        self.rating_num -= 1
        db.session.delete(review)
        db.session.flush()

        return review

    def remove_review_by_id(self, review_id: int):
        stmt = db.select(Review).where(Review.id == review_id)
        review = db.session.execute(stmt).scalar_one_or_none()
        if not review:
            return
        self.remove_review(review)


    @property
    def rating(self):
        if self.rating_num > 0:
            return self.rating_sum / self.rating_num
        return 0

    @property
    def html_description(self):
        return markdown.markdown(self.description)

class Review(db.Model):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    book: Mapped["Book"] = relationship()
    user: Mapped["User"] = relationship()

    @property
    def html_text(self):
        return markdown.markdown(self.text)

collection_book = Table(
    'collection_book',
    db.Model.metadata,
    Column('collection_id', Integer, ForeignKey('collections.id', ondelete='CASCADE'), primary_key=True),
    Column('book_id', Integer, ForeignKey('books.id', ondelete='CASCADE'), primary_key=True)
)


class Collection(db.Model):
    __tablename__ = 'collections'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    user: Mapped["User"] = relationship()
    books: Mapped[List["Book"]] = relationship(
        secondary=collection_book,
        lazy="selectin"
    )

