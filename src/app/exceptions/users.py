class EmailFormatError(ValueError):
    """Exception raised for invalid email format."""

    def __init__(self) -> None:
        super().__init__("Invalid email format.")


class NameFormatError(ValueError):
    """Exception raised for invalid user name format."""

    def __init__(self) -> None:
        super().__init__("Invalid user name format.")


class WeakPasswordError(ValueError):
    """Exception raised for weak passwords."""

    def __init__(self) -> None:
        super().__init__("Password is too short.")


class UserExistsError(ValueError):
    """Exception raised when trying to create a user that already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(f"User {email} already exists.")


class UserNotFoundError(ValueError):
    """Exception raised when a user is not found."""

    def __init__(self, email: str) -> None:
        super().__init__(f"User {email} not found.")


class InvalidPasswordError(ValueError):
    """Exception raised for invalid password."""

    def __init__(self) -> None:
        super().__init__("Invalid password.")
