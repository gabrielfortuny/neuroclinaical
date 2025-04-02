from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    p_hash = generate_password_hash(password, "pbkdf2:sha256:600000")
    return p_hash


def verify_password(password: str, p_hash: str) -> bool:
    return check_password_hash(p_hash, password)
