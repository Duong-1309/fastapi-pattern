import subprocess
import shlex
import jwt
from typing import Optional
from datetime import datetime, timedelta

# Thuật toán
ALGORITHM = "HS256"
# Thời gian tồn tại của access token
ACCESS_TOKEN_EXPIRE_MINUTES = 3000


def get_secret_key():
    # TODO: Need to learn more
    "Get secret key with lib openssl and subprocess"
    cmd = "openssl rand -hex 16"
    completed_process = subprocess.run(shlex.split(cmd), capture_output=True)
    return completed_process.stdout.decode(encoding='utf-8').strip('\n')


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    secret_key=None
):
    """Returns token and secret key for decoding
    Args:
        data (dict): data to be encoded
        expires_delta (timedelta): Time of token life
        secret_key (str): secret key for encoding/decoding token
    Return
        tuple: (encode JWT, SECRET_KEY)
    """
    SECRET_KEY = get_secret_key()
    data_to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_encode.update({"exp": expire})
    if not secret_key:
        encode_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encode_jwt, SECRET_KEY
    encode_jwt = jwt.encode(data_to_encode, secret_key, algorithm=ALGORITHM)
    return encode_jwt, secret_key


def is_expired(encode_jwt, secret_key):
    """Check if the token has expired or not
    Args:
        encode_jwt (str): JWT token
        secret_key (str): key for decoding JWT token
    Returns:
        bool
    """
    try:
        jwt.decode(encode_jwt, secret_key, algorithms=ALGORITHM)
    except Exception:
        return True
    return False


def get_data_from_access_token(encode_jwt, secret_key):
    """Decoding and return data from JWT token
    Args:
        encode_jwt (str): JWT token
        secret_key (str): key for decoding JWT token
    Returns:
        dict
    """
    return jwt.decode(encode_jwt, secret_key, algorithms=ALGORITHM)
