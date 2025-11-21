import bcrypt
from datetime import timedelta, datetime
from src.config import Config
import jwt
import uuid
import logging

ACCESS_TOKEN_EXPIRY = 3600

def generate_passwd_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password_bytes, salt)
    return hash.decode('utf-8')

def verify_password(password: str, hash: str) -> bool:
    password_bytes = password.encode('utf-8')
    hash_bytes = hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)

def create_access_token(user_data:dict,expiry:timedelta= None, refresh:bool=False):
    payload = {}
    
    payload['user']= user_data
    payload['exp']= datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload['jti'] = str(uuid.uuid4())
    
    payload['refresh'] = refresh

    token = jwt.encode(
        payload= payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )
    
    return token

def decode_token(token:str) -> dict:
    try:
        token_data = jwt.decode(
            jwt= token,
            key= Config.JWT_SECRET,
            algorithms= [Config.JWT_ALGORITHM]
        )
        
        return token_data
    
    except jwt.PyJWTError as e:
        logging.error(f"Token decoding error: {e}")
        return None