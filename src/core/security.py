import bcrypt

def hash_password(password: str) -> str:
    """Генерирует безопасный хэш из строки пароля с помощью чистого bcrypt."""
    # Переводим пароль в байты
    password_bytes = password.encode('utf-8')

    # Генерируем соль и хэшируем
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    # Декодируем обратно в строку для сохранения в текстовое поле БД
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли введенный пароль сохраненному хэшу."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    # Функция hashpw сама поймет соль из хэша и сравнит их
    return bcrypt.checkpw(password_bytes, hashed_bytes)
