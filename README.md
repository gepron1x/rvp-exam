# Экзаменационное задание по РВП, Вариант 2

Пронюк Георгий Ярославович, гр. 241-326

## Запуск приложения

```bash
docker compose up
```

Либо в venv:

```bash
pip install -r requirements.txt
flask db upgrade
python init_db.py
python run.py
```

## Пользователи

1. admin:password - Администратор
2. moderator:password - Модератор
3. user:password - Пользователь