from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Role, Genre, User

app = create_app()

with app.app_context():
    try:
        if Role.query.first() is None:
            admin_role = Role(name='Администратор', description='Описание администратора')
            moderator_role = Role(name='Модератор', description='Описание модератора')
            default_role = Role(name='Пользователь', description='Описание пользователя')
            db.session.add_all([admin_role, moderator_role, default_role])
            db.session.flush()
            admin_user = User(login='admin',
                              password_hash=generate_password_hash('password'),
                              first_name='Георгий',
                              last_name='Пронюк',
                              middle_name='Ярославович',
                              role=admin_role
                              )

            moderator_user = User(login='moderator',
                                  password_hash=generate_password_hash('password'),
                                  first_name='Григорий',
                                  last_name='Пронюк',
                                  middle_name='Ярославович',
                                  role=moderator_role
                                  )

            user = User(login='user',
                        password_hash=generate_password_hash('password'),
                        first_name='Егор',
                        last_name='Пронюк',
                        middle_name='Ярославович',
                        role=default_role
                        )

            db.session.add_all([admin_user, moderator_user, user])
            db.session.flush()

        if Genre.query.first() is None:
            book_genres = [
                "Фантастика",
                "Фэнтези",
                "Детектив",
                "Триллер",
                "Роман",
                "Ужасы",
                "Исторический роман",
                "Биография",
                "Научпоп",
                "Поэзия"
            ]

            db.session.add_all([Genre(name=name) for name in book_genres])
            db.session.flush()
        db.session.commit()
        print("Database initialized")
    except Exception as e:
        db.session.rollback()
        print(f"Database init failed, {e}")
