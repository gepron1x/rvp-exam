import hashlib
import os

from flask import current_app
from sqlalchemy import func
from werkzeug.datastructures.file_storage import FileStorage
from werkzeug.utils import secure_filename

from app import db, config
from app.models import Cover, Book


def get_full_path(filename):
    return os.path.join(config.UPLOAD_FOLDER, filename)

def create_cover(file: FileStorage) -> Cover:
    file_content = file.read()
    md5_hash = hashlib.md5(file_content).hexdigest()
    filename = secure_filename(file.filename)

    stmt = db.select(Cover).where(Cover.md5_hash == md5_hash)
    existing_cover = db.session.execute(stmt).scalar_one_or_none()

    if existing_cover:
        return existing_cover

    unique_filename = f"{md5_hash}_{filename}"

    cover = Cover(
        file_name=unique_filename,
        mime=file.content_type,
        md5_hash=md5_hash
    )
    db.session.add(cover)
    db.session.flush()

    return cover

def save_cover(cover: Cover, file: FileStorage):
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    full_path = get_full_path(cover.file_name)
    if os.path.exists(full_path):
        return
    file.seek(0)
    file.save(full_path)

def delete_cover(cover: Cover) -> bool:
    stmt = db.select(func.count()).select_from(Book).where(Book.cover_id == cover.id)
    count = db.session.execute(stmt).scalar()
    should_delete = count < 1
    if should_delete:
        db.session.delete(cover)
        db.session.flush()
    return should_delete

def delete_file(cover: Cover):
    os.remove(get_full_path(cover.file_name))
