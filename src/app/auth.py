from passlib.context import CryptContext

JWT_SECRET_KEY = "1231232321"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

# the logic will be added later
def get_current_user() -> str:
    """Mock function to get the current user's email."""
    return "g.popov@innopolis.university"
