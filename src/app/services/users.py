from sqlalchemy.orm import Session

from src.app.infrastructure.adapters.events_adapter import EventsAdapter
from src.app.infrastructure.adapters.users_adapter import UsersAdapter
from src.app.services.models.users import AccessToken, UserCreate, UserLogin


class UserService:
    """Service layer for the Users."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventsAdapter(db)
        self.users = UsersAdapter(db)

    def register(self, user: UserCreate) -> AccessToken:
        """Register user."""
        self.users.validate_user_email(user.email)
        self.users.validate_user_name(user.name)
        self.users.validate_password_lenght(user.password)
        user = self.users.create_user(user.email, user.name, user.password)
        token = self.users.get_access_token(user)
        self.db.commit()
        return AccessToken(access_token=token)

    def login(self, user: UserLogin) -> AccessToken:
        """Login and provide access token."""
        system_user = self.users.get_user(user.email)
        self.users.verify_password(system_user, user.password)
        token = self.users.get_access_token(system_user)
        return AccessToken(access_token=token)
