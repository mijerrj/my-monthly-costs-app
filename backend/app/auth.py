import os
import jwt
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from dotenv import load_dotenv
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt  # PyJWT

load_dotenv()

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)

def hash_password(password):
    return bcrypt.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

 def decode_jwt_token(token: str):
     try:
         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
         user_id: int = payload.get("user_id")
         if user_id is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="Invalid token payload")
         return user_id
     except jwt.PyJWTError:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                             detail="Could not validate credentials")
