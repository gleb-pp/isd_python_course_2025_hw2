from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from datetime import datetime, timezone

JWT_SECRET_KEY = "1231232321"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
PWD_MIN_LENGTH = 8
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        expire_timestamp = payload.get("exp")
        user_email = payload.get("email")

        # checking the fields
        if expire_timestamp is None or user_email is None:
            raise ValueError("Invalid token structure")

        # checking token expiration time
        if datetime.now(tz=timezone.utc) > datetime.fromtimestamp(expire_timestamp, tz=timezone.utc):
            raise ValueError("Token expired")

    except (JWTError, ValueError) as e:
        detail = str(e) if str(e) else "Invalid token"
        raise HTTPException(status_code=401, detail=detail) from e

    return user_email
