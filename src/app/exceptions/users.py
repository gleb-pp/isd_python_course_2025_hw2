class UserException(Exception):
    """Base exception for user-related errors."""
    pass

class EmailFormatError(UserException):
    """Exception raised for invalid email format."""

    def __init__(self) -> None:
        super().__init__("Invalid email format.")

class NameFormatError(UserException):
    """Exception raised for invalid user name format."""

    def __init__(self) -> None:
        super().__init__("Invalid user name format.")

class WeakPasswordError(UserException):
    """Exception raised for weak passwords."""

    def __init__(self) -> None:
        super().__init__("Password is too short.")

class UserExistsError(UserException):
    """Exception raised when trying to create a user that already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(f"User {email} already exists.")

class UserNotFoundError(UserException):
    """Exception raised when a user is not found."""

    def __init__(self, email: str) -> None:
        super().__init__(f"User {email} not found.")

class InvalidPasswordError(UserException):
    """Exception raised for invalid password."""

    def __init__(self) -> None:
        super().__init__("Invalid password.")
