# from unittest.mock import MagicMock, patch

# from fastapi.testclient import TestClient

# import src.app.domain.exceptions.bookings as booking_errors
# import src.app.domain.exceptions.events as event_errors
# import src.app.domain.exceptions.users as user_errors
# from src.app.auth import get_current_user
# from src.app.db import get_db
# from src.app.infrastructure.db_models.bookings import BookingDB
# from src.app.infrastructure.db_models.events import EventDB
# from src.app.infrastructure.db_models.users import UserDB
# from src.app.main import app

# client = TestClient(app)

# HTTP_200_OK = 200
# HTTP_409_CONFLICT = 409
# HTTP_401_UNAUTHORIZED = 401
# HTTP_403_FORBIDDEN = 403
# HTTP_400_BAD_REQUEST = 400
# HTTP_422_UNPROCESSABLE_ENTITY = 422
# HTTP_404_NOT_FOUND = 404


# def create_mock_event(**kwargs: object) -> MagicMock:
#     """Create a mock EventDB object for testing."""
#     mock_event = MagicMock(spec=EventDB)
#     for key, value in kwargs.items():
#         setattr(mock_event, key, value)
#     return mock_event


# def create_mock_booking(**kwargs: object) -> MagicMock:
#     """Create a mock BookingDB object for testing."""
#     mock_booking = MagicMock(spec=BookingDB)
#     for key, value in kwargs.items():
#         setattr(mock_booking, key, value)
#     return mock_booking


# def create_mock_user(**kwargs: object) -> MagicMock:
#     """Create a mock UserDB object for testing."""
#     mock_user = MagicMock(spec=UserDB)
#     for key, value in kwargs.items():
#         setattr(mock_user, key, value)
#     return mock_user


# def test__get_all_users__success() -> None:
#     """Test to get all the system users."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_user = create_mock_user()
#     user_list = [
#         create_mock_user(email="g.popov@inno.ru", name="Gleb"),
#         create_mock_user(email="a.popov@inno.ru", name="Arthur"),
#     ]

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.user_logic.get_all_users",
#             return_value=user_list,
#         ) as mock_get_all_users,
#     ):
#         response = client.get("/admin/users")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_get_all_users.assert_called_once_with(mock_db)
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == [
#         {"email": "g.popov@inno.ru", "name": "Gleb"},
#         {"email": "a.popov@inno.ru", "name": "Arthur"},
#     ]


# def test__get_all_users__random_user() -> None:
#     """Attempt to get all the system users from the random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.user_logic.get_all_users"
#         ) as mock_get_all_users,
#     ):
#         response = client.get("/admin/users")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_not_called()
#     mock_get_all_users.assert_not_called()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__get_all_users__not_admin() -> None:
#     """Attempt to get all the system users from non-administrator."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin",
#             side_effect=user_errors.AdminRoleRequiredError("g.popov@inno.ru"),
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.user_logic.get_all_users"
#         ) as mock_get_all_users,
#     ):
#         response = client.get("/admin/users")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_get_all_users.assert_not_called()
#     assert response.status_code == HTTP_403_FORBIDDEN


# def test__create_user__success() -> None:
#     """Test to create user from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     new_user = {"email": "a.popov@inno.ru", "name": "Arthur", "password": "12345678"}
#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_email"
#         ) as mock_validate_user_email,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_name"
#         ) as mock_validate_user_name,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_password_lenght"
#         ) as mock_validate_password_lenght,
#         patch(
#             "src.app.presentation.users.user_logic.create_user", return_value=mock_user
#         ) as mock_create_user,
#     ):
#         response = client.post("/admin/users", json=new_user)

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_validate_user_email.assert_called_once_with(new_user["email"])
#     mock_validate_user_name.assert_called_once_with(new_user["name"])
#     mock_validate_password_lenght.assert_called_once_with(new_user["password"])
#     mock_create_user.assert_called_once_with(
#         new_user["email"], new_user["name"], new_user["password"], mock_db
#     )
#     mock_db.commit.assert_called_once()
#     mock_db.rollback.assert_not_called()
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == {"success": True}


# def test__create_user__random_user() -> None:
#     """Attempt to create user from the random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     new_user = {"email": "a.popov@inno.ru", "name": "Arthur", "password": "12345678"}

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_email"
#         ) as mock_validate_user_email,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_name"
#         ) as mock_validate_user_name,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_password_lenght"
#         ) as mock_validate_password_lenght,
#         patch("src.app.presentation.users.user_logic.create_user") as mock_create_user,
#     ):
#         response = client.post("/admin/users", json=new_user)

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_not_called()
#     mock_validate_user_email.assert_not_called()
#     mock_validate_user_name.assert_not_called()
#     mock_validate_password_lenght.assert_not_called()
#     mock_create_user.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__create_user__non_admin() -> None:
#     """Attempt to create user from non-admin."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     new_user = {"email": "a.popov@inno.ru", "name": "Arthur", "password": "12345678"}
#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin",
#             side_effect=user_errors.AdminRoleRequiredError("g.popov@inno.ru"),
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_email"
#         ) as mock_validate_user_email,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_name"
#         ) as mock_validate_user_name,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_password_lenght"
#         ) as mock_validate_password_lenght,
#         patch(
#             "src.app.presentation.users.user_logic.create_user", return_value=mock_user
#         ) as mock_create_user,
#     ):
#         response = client.post("/admin/users", json=new_user)

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_validate_user_email.assert_not_called()
#     mock_validate_user_name.assert_not_called()
#     mock_validate_password_lenght.assert_not_called()
#     mock_create_user.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_403_FORBIDDEN


# def test__create_user__invalid_email() -> None:
#     """Attempt to create user with invalid email from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     new_user = {"email": "a.popov@inno.ru", "name": "Arthur", "password": "12345678"}
#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_email",
#             side_effect=user_errors.EmailFormatError,
#         ) as mock_validate_user_email,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_name"
#         ) as mock_validate_user_name,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_password_lenght"
#         ) as mock_validate_password_lenght,
#         patch(
#             "src.app.presentation.users.user_logic.create_user", return_value=mock_user
#         ) as mock_create_user,
#     ):
#         response = client.post("/admin/users", json=new_user)

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_validate_user_email.assert_called_once_with(new_user["email"])
#     mock_validate_user_name.assert_not_called()
#     mock_validate_password_lenght.assert_not_called()
#     mock_create_user.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


# def test__create_user__invalid_name() -> None:
#     """Attempt to create user with invalid name from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     new_user = {"email": "a.popov@inno.ru", "name": "Arthur", "password": "12345678"}
#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_email"
#         ) as mock_validate_user_email,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_name",
#             side_effect=user_errors.NameFormatError,
#         ) as mock_validate_user_name,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_password_lenght"
#         ) as mock_validate_password_lenght,
#         patch(
#             "src.app.presentation.users.user_logic.create_user", return_value=mock_user
#         ) as mock_create_user,
#     ):
#         response = client.post("/admin/users", json=new_user)

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_validate_user_email.assert_called_once_with(new_user["email"])
#     mock_validate_user_name.assert_called_once_with(new_user["name"])
#     mock_validate_password_lenght.assert_not_called()
#     mock_create_user.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


# def test__create_user__weak_password() -> None:
#     """Attempt to create user with too short password from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     new_user = {"email": "a.popov@inno.ru", "name": "Arthur", "password": "12345678"}
#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_email"
#         ) as mock_validate_user_email,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_name"
#         ) as mock_validate_user_name,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_password_lenght",
#             side_effect=user_errors.WeakPasswordError,
#         ) as mock_validate_password_lenght,
#         patch(
#             "src.app.presentation.users.user_logic.create_user", return_value=mock_user
#         ) as mock_create_user,
#     ):
#         response = client.post("/admin/users", json=new_user)

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_validate_user_email.assert_called_once_with(new_user["email"])
#     mock_validate_user_name.assert_called_once_with(new_user["name"])
#     mock_validate_password_lenght.assert_called_once_with(new_user["password"])
#     mock_create_user.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY


# def test__create_user__user_exists() -> None:
#     """Attempt to create a user that already exists from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     new_user = {"email": "a.popov@inno.ru", "name": "Arthur", "password": "12345678"}
#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_email"
#         ) as mock_validate_user_email,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_user_name"
#         ) as mock_validate_user_name,
#         patch(
#             "src.app.presentation.admins.user_logic.validate_password_lenght"
#         ) as mock_validate_password_lenght,
#         patch(
#             "src.app.presentation.users.user_logic.create_user",
#             side_effect=user_errors.UserExistsError(new_user["email"]),
#         ) as mock_create_user,
#     ):
#         response = client.post("/admin/users", json=new_user)

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_validate_user_email.assert_called_once_with(new_user["email"])
#     mock_validate_user_name.assert_called_once_with(new_user["name"])
#     mock_validate_password_lenght.assert_called_once_with(new_user["password"])
#     mock_create_user.assert_called_once_with(
#         new_user["email"], new_user["name"], new_user["password"], mock_db
#     )
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_409_CONFLICT


# def test__delete_user__success() -> None:
#     """Test to delete user from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_admin = create_mock_user()
#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=[mock_admin, mock_user],
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.user_logic.delete_user") as mock_delete_user,
#     ):
#         response = client.delete("/admin/users/a.popov@inno.ru")

#     assert mock_get_user.call_count == 1 + 1
#     mock_get_user.assert_any_call("g.popov@inno.ru", mock_db)
#     mock_get_user.assert_any_call("a.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_delete_user.assert_called_once_with(mock_user, mock_db)
#     mock_db.commit.assert_called_once()
#     mock_db.rollback.assert_not_called()
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == {"success": True}


# def test__delete_user__random_user() -> None:
#     """Attempt to delete user from random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.user_logic.delete_user") as mock_delete_user,
#     ):
#         response = client.delete("/admin/users/a.popov@inno.ru")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_not_called()
#     mock_delete_user.assert_not_called()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__delete_user__non_admin() -> None:
#     """Attempt to delete user from non-admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_admin = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_admin
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin",
#             side_effect=user_errors.AdminRoleRequiredError("g.popov@inno.ru"),
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.user_logic.delete_user") as mock_delete_user,
#     ):
#         response = client.delete("/admin/users/a.popov@inno.ru")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_delete_user.assert_not_called()
#     assert response.status_code == HTTP_403_FORBIDDEN


# def test__delete_user__not_found() -> None:
#     """Attempts to delete user that does not exist from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_admin = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=[mock_admin, user_errors.UserNotFoundError("a.popov@inno.ru")],
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.user_logic.delete_user") as mock_delete_user,
#     ):
#         response = client.delete("/admin/users/a.popov@inno.ru")

#     assert mock_get_user.call_count == 1 + 1
#     mock_get_user.assert_any_call("g.popov@inno.ru", mock_db)
#     mock_get_user.assert_any_call("a.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_delete_user.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_404_NOT_FOUND


# def test__delete_event__success() -> None:
#     """Test to delete event from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_admin = create_mock_user()
#     mock_event = create_mock_event()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_admin
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.events_logic.get_event",
#             return_value=mock_event,
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.admins.events_logic.delete_event"
#         ) as mock_delete_event,
#     ):
#         response = client.delete("/admin/events/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_called_once_with(1, mock_db)
#     mock_delete_event.assert_called_once_with(mock_event, mock_db)
#     mock_db.commit.assert_called_once()
#     mock_db.rollback.assert_not_called()
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == {"success": True}


# def test__delete_event__random_user() -> None:
#     """Attempt to delete event from random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.events_logic.get_event") as mock_get_event,
#     ):
#         response = client.delete("/admin/events/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_not_called()
#     mock_get_event.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__delete_event__non_admin() -> None:
#     """Attempt to delete event from non-admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_admin = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_admin
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin",
#             side_effect=user_errors.AdminRoleRequiredError("g.popov@inno.ru"),
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.events_logic.get_event") as mock_get_event,
#     ):
#         response = client.delete("/admin/events/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_403_FORBIDDEN


# def test__delete_event__not_found() -> None:
#     """Attempt to delete non-existent event from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_admin = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_admin
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.events_logic.get_event",
#             side_effect=event_errors.EventNotFoundError(1),
#         ) as mock_get_event,
#     ):
#         response = client.delete("/admin/events/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_called_once_with(1, mock_db)
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_404_NOT_FOUND


# def test__create_user_booking__success() -> None:
#     """Test to create booking for another user from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     mock_admin = create_mock_user()
#     mock_guest = create_mock_user()
#     mock_event = create_mock_event()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=[mock_admin, mock_guest],
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.events_logic.get_event",
#             return_value=mock_event,
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.assert_seats_available"
#         ) as mock_assert_seats,
#         patch(
#             "src.app.presentation.admins.bookings_logic.create_booking"
#         ) as mock_create_booking,
#     ):
#         response = client.post("/admin/bookings/5/guest@inno.ru")

#     assert mock_get_user.call_count == 1 + 1
#     mock_get_user.assert_any_call("admin@inno.ru", mock_db)
#     mock_get_user.assert_any_call("guest@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_called_once_with(5, mock_db)
#     mock_assert_seats.assert_called_once_with(mock_event, mock_db)
#     mock_create_booking.assert_called_once_with(mock_event, mock_guest, mock_db)
#     mock_db.commit.assert_called_once()
#     mock_db.rollback.assert_not_called()
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == {"success": True}


# def test__create_user_booking__random_user() -> None:
#     """Attempt to create booking from random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.assert_seats_available"
#         ) as mock_assert_seats,
#         patch(
#             "src.app.presentation.admins.bookings_logic.create_booking"
#         ) as mock_create_booking,
#     ):
#         response = client.post("/admin/bookings/5/guest@inno.ru")

#     mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
#     mock_assert_admin.assert_not_called()
#     mock_get_event.assert_not_called()
#     mock_assert_seats.assert_not_called()
#     mock_create_booking.assert_not_called()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__create_user_booking__non_admin() -> None:
#     """Attempt to create booking from non-admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "user@inno.ru"

#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin",
#             side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.assert_seats_available"
#         ) as mock_assert_seats,
#         patch(
#             "src.app.presentation.admins.bookings_logic.create_booking"
#         ) as mock_create_booking,
#     ):
#         response = client.post("/admin/bookings/5/guest@inno.ru")

#     mock_get_user.assert_called_once_with("user@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_get_event.assert_not_called()
#     mock_assert_seats.assert_not_called()
#     mock_create_booking.assert_not_called()
#     assert response.status_code == HTTP_403_FORBIDDEN


# def test__create_user_booking__guest_not_found() -> None:
#     """Attempt to create booking for non-existent guest."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     mock_admin = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=[mock_admin, user_errors.UserNotFoundError("guest@inno.ru")],
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.assert_seats_available"
#         ) as mock_assert_seats,
#         patch(
#             "src.app.presentation.admins.bookings_logic.create_booking"
#         ) as mock_create_booking,
#     ):
#         response = client.post("/admin/bookings/5/guest@inno.ru")

#     assert mock_get_user.call_count == 1 + 1
#     mock_get_user.assert_any_call("guest@inno.ru", mock_db)
#     mock_get_user.assert_any_call("admin@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_not_called()
#     mock_assert_seats.assert_not_called()
#     mock_create_booking.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_404_NOT_FOUND


# def test__create_user_booking__event_not_found() -> None:
#     """Attempt to create booking for non-existent event."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     mock_admin = create_mock_user()
#     mock_guest = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=[mock_admin, mock_guest],
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.events_logic.get_event",
#             side_effect=event_errors.EventNotFoundError(5),
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.assert_seats_available"
#         ) as mock_assert_seats,
#         patch(
#             "src.app.presentation.admins.bookings_logic.create_booking"
#         ) as mock_create_booking,
#     ):
#         response = client.post("/admin/bookings/5/guest@inno.ru")

#     assert mock_get_user.call_count == 1 + 1
#     mock_get_user.assert_any_call("guest@inno.ru", mock_db)
#     mock_get_user.assert_any_call("admin@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_called_once_with(5, mock_db)
#     mock_assert_seats.assert_not_called()
#     mock_create_booking.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_400_BAD_REQUEST


# def test__create_user_booking__event_full() -> None:
#     """Attempt to create booking when event is full."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     mock_admin = create_mock_user()
#     mock_guest = create_mock_user()
#     mock_event = create_mock_event()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=[mock_admin, mock_guest],
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.events_logic.get_event",
#             return_value=mock_event,
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.assert_seats_available",
#             side_effect=booking_errors.EventFullError(5),
#         ) as mock_assert_seats,
#         patch(
#             "src.app.presentation.admins.bookings_logic.create_booking"
#         ) as mock_create_booking,
#     ):
#         response = client.post("/admin/bookings/5/guest@inno.ru")

#     assert mock_get_user.call_count == 1 + 1
#     mock_get_user.assert_any_call("guest@inno.ru", mock_db)
#     mock_get_user.assert_any_call("admin@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_called_once_with(5, mock_db)
#     mock_assert_seats.assert_called_once_with(mock_event, mock_db)
#     mock_create_booking.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_409_CONFLICT


# def test__delete_user_booking__success() -> None:
#     """Test to delete user booking from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     mock_admin = create_mock_user()
#     mock_guest = create_mock_user()
#     mock_event = create_mock_event()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=[mock_admin, mock_guest],
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.events_logic.get_event",
#             return_value=mock_event,
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.delete_booking"
#         ) as mock_delete_booking,
#     ):
#         response = client.delete("/admin/bookings/5/guest@inno.ru")

#     assert mock_get_user.call_count == 1 + 1
#     mock_get_user.assert_any_call("admin@inno.ru", mock_db)
#     mock_get_user.assert_any_call("guest@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_called_once_with(5, mock_db)
#     mock_delete_booking.assert_called_once_with(mock_event, mock_guest, mock_db)
#     mock_db.commit.assert_called_once()
#     mock_db.rollback.assert_not_called()
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == {"success": True}


# def test__delete_user_booking__random_user() -> None:
#     """Attempt to delete user booking from random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.delete_booking"
#         ) as mock_delete_booking,
#     ):
#         response = client.delete("/admin/bookings/5/guest@inno.ru")

#     mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
#     mock_assert_admin.assert_not_called()
#     mock_get_event.assert_not_called()
#     mock_delete_booking.assert_not_called()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__delete_user_booking__non_admin() -> None:
#     """Attempt to delete user booking from non-admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "user@inno.ru"

#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin",
#             side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.delete_booking"
#         ) as mock_delete_booking,
#     ):
#         response = client.delete("/admin/bookings/5/guest@inno.ru")

#     mock_get_user.assert_called_once_with("user@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_get_event.assert_not_called()
#     mock_delete_booking.assert_not_called()
#     assert response.status_code == HTTP_403_FORBIDDEN


# def test__delete_user_booking__guest_not_found() -> None:
#     """Attempt to delete booking for non-existent guest."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     mock_admin = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=[mock_admin, user_errors.UserNotFoundError("guest@inno.ru")],
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.delete_booking"
#         ) as mock_delete_booking,
#     ):
#         response = client.delete("/admin/bookings/5/guest@inno.ru")

#     assert mock_get_user.call_count == 1 + 1
#     mock_get_user.assert_any_call("admin@inno.ru", mock_db)
#     mock_get_user.assert_any_call("guest@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_not_called()
#     mock_delete_booking.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_404_NOT_FOUND


# def test__delete_user_booking__event_not_found() -> None:
#     """Attempt to delete booking for non-existent event."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     mock_admin = create_mock_user()
#     mock_guest = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=[mock_admin, mock_guest],
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.events_logic.get_event",
#             side_effect=event_errors.EventNotFoundError(5),
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.delete_booking"
#         ) as mock_delete_booking,
#     ):
#         response = client.delete("/admin/bookings/5/guest@inno.ru")

#     assert mock_get_user.call_count == 1 + 1
#     mock_get_user.assert_any_call("admin@inno.ru", mock_db)
#     mock_get_user.assert_any_call("guest@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_called_once_with(5, mock_db)
#     mock_delete_booking.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_400_BAD_REQUEST


# def test__get_event_participants__success() -> None:
#     """Test to get event participants from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     mock_admin = create_mock_user()
#     mock_event = create_mock_event()
#     participants_emails = ["user1@inno.ru", "user2@inno.ru", "user3@inno.ru"]

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_admin
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.events_logic.get_event",
#             return_value=mock_event,
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.get_event_participants",
#             return_value=participants_emails,
#         ) as mock_get_participants,
#     ):
#         response = client.get("/admin/bookings/5")

#     mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_called_once_with(5, mock_db)
#     mock_get_participants.assert_called_once_with(mock_event, mock_db)
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == {"participants_emails": participants_emails}


# def test__get_event_participants__random_user() -> None:
#     """Attempt to get event participants from random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.get_event_participants"
#         ) as mock_get_participants,
#     ):
#         response = client.get("/admin/bookings/5")

#     mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
#     mock_assert_admin.assert_not_called()
#     mock_get_event.assert_not_called()
#     mock_get_participants.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__get_event_participants__non_admin() -> None:
#     """Attempt to get event participants from non-admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "user@inno.ru"

#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin",
#             side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
#         ) as mock_assert_admin,
#         patch("src.app.presentation.admins.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.get_event_participants"
#         ) as mock_get_participants,
#     ):
#         response = client.get("/admin/bookings/5")

#     mock_get_user.assert_called_once_with("user@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_get_event.assert_not_called()
#     mock_get_participants.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_403_FORBIDDEN


# def test__get_event_participants__event_not_found() -> None:
#     """Attempt to get participants for non-existent event."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     mock_admin = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_admin
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.events_logic.get_event",
#             side_effect=event_errors.EventNotFoundError(5),
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.admins.bookings_logic.get_event_participants"
#         ) as mock_get_participants,
#     ):
#         response = client.get("/admin/bookings/5")

#     mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_event.assert_called_once_with(5, mock_db)
#     mock_get_participants.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_400_BAD_REQUEST


# def test__get_bookings__success() -> None:
#     """Test to get all bookings from admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     mock_admin = create_mock_user()
#     mock_bookings = [
#         create_mock_booking(event_id=1, user_email="user1@inno.ru"),
#         create_mock_booking(event_id=2, user_email="user2@inno.ru"),
#         create_mock_booking(event_id=1, user_email="user3@inno.ru"),
#     ]

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_admin
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.bookings_logic.get_all_bookings",
#             return_value=mock_bookings,
#         ) as mock_get_all_bookings,
#     ):
#         response = client.get("/admin/bookings")

#     mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_admin)
#     mock_get_all_bookings.assert_called_once_with(mock_db)
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == [
#         {"event_id": 1, "user_email": "user1@inno.ru"},
#         {"event_id": 2, "user_email": "user2@inno.ru"},
#         {"event_id": 1, "user_email": "user3@inno.ru"},
#     ]


# def test__get_bookings__random_user() -> None:
#     """Attempt to get all bookings from random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "admin@inno.ru"

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("admin@inno.ru"),
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin"
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.bookings_logic.get_all_bookings"
#         ) as mock_get_all_bookings,
#     ):
#         response = client.get("/admin/bookings")

#     mock_get_user.assert_called_once_with("admin@inno.ru", mock_db)
#     mock_assert_admin.assert_not_called()
#     mock_get_all_bookings.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__get_bookings__non_admin() -> None:
#     """Attempt to get all bookings from non-admin account."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "user@inno.ru"

#     mock_user = create_mock_user()

#     with (
#         patch(
#             "src.app.presentation.admins.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.admins.user_logic.assert_user_is_admin",
#             side_effect=user_errors.AdminRoleRequiredError("user@inno.ru"),
#         ) as mock_assert_admin,
#         patch(
#             "src.app.presentation.admins.bookings_logic.get_all_bookings"
#         ) as mock_get_all_bookings,
#     ):
#         response = client.get("/admin/bookings")

#     mock_get_user.assert_called_once_with("user@inno.ru", mock_db)
#     mock_assert_admin.assert_called_once_with(mock_user)
#     mock_get_all_bookings.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_403_FORBIDDEN
