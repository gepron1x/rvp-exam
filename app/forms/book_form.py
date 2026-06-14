from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from datetime import datetime


class BookForm(FlaskForm):
    title = StringField('Название', validators=[
        DataRequired(message='Название обязательно'),
        Length(max=100, message='Название не должно превышать 100 символов')
    ])

    description = TextAreaField('Описание', validators=[
        DataRequired(message='Описание обязательно')
    ])

    year = IntegerField('Год издания', validators=[
        DataRequired(message='Год издания обязателен'),
        NumberRange(min=1000, max=datetime.now().year,
                    message=f'Год должен быть между 1000 и {datetime.now().year}')
    ])

    publisher = StringField('Издательство', validators=[
        DataRequired(message='Издательство обязательно'),
        Length(max=100, message='Издательство не должно превышать 100 символов')
    ])

    pages = IntegerField('Количество страниц', validators=[
        DataRequired(message='Количество страниц обязательно'),
        NumberRange(min=1, message='Количество страниц должно быть положительным')
    ])

    genres = SelectMultipleField('Жанры', choices=[], validators=[
        DataRequired(message='Выберите хотя бы один жанр')
    ])

    cover = FileField('Обложка', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
                    message='Разрешены только изображения (JPEG, PNG, GIF)')
    ])

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        from app.models import Genre
        from app import db
        from sqlalchemy import select

        stmt = select(Genre).order_by(Genre.name)
        genres = db.session.execute(stmt).scalars().all()
        self.genres.choices = [(g.id, g.name) for g in genres]

    def validate_pages(self, field):
        if field.data <= 0:
            raise ValidationError('Количество страниц должно быть положительным')
        if field.data > 10000:
            raise ValidationError('Количество страниц не может превышать 10000')