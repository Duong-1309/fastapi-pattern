from passlib.context import CryptContext


pwd_context = CryptContext('bcrypt', deprecated='auto')

def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)

def get_password_hashed(password):
    return pwd_context.hash(password)
