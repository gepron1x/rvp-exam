from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class ReviewForm(FlaskForm):
    rating = SelectField(
        'Оценка',
        choices=[
            (5, '5 — Отлично'),
            (4, '4 — Хорошо'),
            (3, '3 — Удовлетворительно'),
            (2, '2 — Неудовлетворительно'),
            (1, '1 — Плохо'),
            (0, '0 — Ужасно')
        ],
        default=5,
        coerce=int,
        validators=[DataRequired()]
    )

    text = TextAreaField(
        'Текст рецензии',
        validators=[
            Optional(),
            Length(max=5000, message="Текст рецензии слишком длинный (максимум 5000 символов)")
        ],
        render_kw={"rows": 10, "placeholder": "Напишите вашу рецензию здесь... Поддерживается Markdown"}
    )

    submit = SubmitField('Опубликовать рецензию')