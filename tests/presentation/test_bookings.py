# from unittest.mock import MagicMock, patch

# from fastapi.testclient import TestClient

# import src.app.domain.exceptions.bookings as booking_errors
# import src.app.domain.exceptions.events as event_errors
# import src.app.domain.exceptions.users as user_errors
# from src.app.auth import get_current_user
# from src.app.db import get_db
# from src.app.infrastructure.db_models.events import EventDB
# from src.app.infrastructure.db_models.users import UserDB
# from src.app.main import app

# client = TestClient(app)

# HTTP_200_OK = 200
# HTTP_409_CONFLICT = 409
# HTTP_401_UNAUTHORIZED = 401
# HTTP_403_FORBIDDEN = 403
# HTTP_400_BAD_REQUEST = 400


# def create_mock_event(**kwargs: object) -> MagicMock:
#     """Create a mock EventDB object for testing."""
#     mock_event = MagicMock(spec=EventDB)
#     for key, value in kwargs.items():
#         setattr(mock_event, key, value)
#     return mock_event


# def create_mock_user(**kwargs: object) -> MagicMock:
#     """Create a mock UserDB object for testing."""
#     mock_user = MagicMock(spec=UserDB)
#     for key, value in kwargs.items():
#         setattr(mock_user, key, value)
#     return mock_user


# def test__create_booking__success() -> None:
#     """Test successful booking creation."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_user = create_mock_user()
#     mock_event = create_mock_event()

#     with (
#         patch(
#             "src.app.presentation.bookings.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.bookings.events_logic.get_event",
#             return_value=mock_event,
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.assert_seats_available"
#         ) as mock_assert_seats_available,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.create_booking"
#         ) as mock_create_booking,
#     ):
#         response = client.post("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_called_once_with(1, mock_db)
#     mock_assert_seats_available.assert_called_once_with(mock_event, mock_db)
#     mock_create_booking.assert_called_once_with(mock_event, mock_user, mock_db)
#     mock_db.commit.assert_called_once()
#     mock_db.rollback.assert_not_called()
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == {"success": True}


# def test__create_booking__random_user() -> None:
#     """Attempt to create a booking from random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     with (
#         patch(
#             "src.app.presentation.bookings.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
#         ) as mock_get_user,
#         patch("src.app.presentation.bookings.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.assert_seats_available"
#         ) as mock_assert_seats_available,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.create_booking"
#         ) as mock_create_booking,
#     ):
#         response = client.post("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_not_called()
#     mock_assert_seats_available.assert_not_called()
#     mock_create_booking.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assassert_called_once()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__create_booking__no_event() -> None:
#     """Attempt to create a booking for a non-existing event."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     with (
#         patch("src.app.presentation.bookings.user_logic.get_user") as mock_get_user,
#         patch(
#             "src.app.presentation.bookings.events_logic.get_event",
#             side_effect=event_errors.EventNotFoundError(1),
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.assert_seats_available"
#         ) as mock_assert_seats_available,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.create_booking"
#         ) as mock_create_booking,
#     ):
#         response = client.post("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_called_once_with(1, mock_db)
#     mock_assert_seats_available.assert_not_called()
#     mock_create_booking.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assassert_called_once()
#     assert response.status_code == HTTP_400_BAD_REQUEST


# def test__create_booking__no_seats() -> None:
#     """Attempt to create a booking for a full event."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_event = create_mock_event()

#     with (
#         patch("src.app.presentation.bookings.user_logic.get_user") as mock_get_user,
#         patch(
#             "src.app.presentation.bookings.events_logic.get_event",
#             return_value=mock_event,
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.assert_seats_available",
#             side_effect=booking_errors.EventFullError(1),
#         ) as mock_assert_seats_available,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.create_booking"
#         ) as mock_create_booking,
#     ):
#         response = client.post("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_called_once_with(1, mock_db)
#     mock_assert_seats_available.assert_called_once_with(mock_event, mock_db)
#     mock_create_booking.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assassert_called_once()
#     assert response.status_code == HTTP_409_CONFLICT


# def test__delete_booking__success() -> None:
#     """Test successful booking deletion."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_user = create_mock_user()
#     mock_event = create_mock_event()

#     with (
#         patch(
#             "src.app.presentation.bookings.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.bookings.events_logic.get_event",
#             return_value=mock_event,
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.delete_booking"
#         ) as mock_delete_booking,
#     ):
#         response = client.delete("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_called_once_with(1, mock_db)
#     mock_delete_booking.assert_called_once_with(mock_event, mock_user, mock_db)
#     mock_db.commit.assert_called_once()
#     mock_db.rollback.assert_not_called()
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == {"success": True}


# def test__delete_booking__random_user() -> None:
#     """Attempt to delete a booking from random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     with (
#         patch(
#             "src.app.presentation.bookings.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
#         ) as mock_get_user,
#         patch("src.app.presentation.bookings.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.delete_booking"
#         ) as mock_delete_booking,
#     ):
#         response = client.delete("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_not_called()
#     mock_delete_booking.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__delete_booking__no_event() -> None:
#     """Attempt to delete a booking for a non-existing event."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     with (
#         patch("src.app.presentation.bookings.user_logic.get_user") as mock_get_user,
#         patch(
#             "src.app.presentation.bookings.events_logic.get_event",
#             side_effect=event_errors.EventNotFoundError(1),
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.delete_booking"
#         ) as mock_delete_booking,
#     ):
#         response = client.delete("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_called_once_with(1, mock_db)
#     mock_delete_booking.assert_not_called()
#     mock_db.commit.assert_not_called()
#     mock_db.rollback.assert_called_once()
#     assert response.status_code == HTTP_400_BAD_REQUEST


# def test__get_event_participants__success() -> None:
#     """Test to get the list of event's participants."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_user = create_mock_user()
#     mock_event = create_mock_event()
#     participants = ["g.popov@inno.ru", "a.popov@inno.ru"]

#     with (
#         patch(
#             "src.app.presentation.bookings.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.bookings.events_logic.get_event",
#             return_value=mock_event,
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.events_logic.assert_user_is_organizer"
#         ) as mock_assert_organizer,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.get_event_participants",
#             return_value=participants,
#         ) as mock_get_event_participants,
#     ):
#         response = client.get("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_called_once_with(1, mock_db)
#     mock_assert_organizer.assert_called_once_with(mock_event, mock_user)
#     mock_get_event_participants.assert_called_once_with(mock_event, mock_db)
#     assert response.status_code == HTTP_200_OK
#     assert response.json() == {
#         "participants_emails": ["g.popov@inno.ru", "a.popov@inno.ru"]
#     }


# def test__get_event_participants__random_user() -> None:
#     """Attempt to get the list of event's participants from a random email."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     with (
#         patch(
#             "src.app.presentation.bookings.user_logic.get_user",
#             side_effect=user_errors.UserNotFoundError("g.popov@inno.ru"),
#         ) as mock_get_user,
#         patch("src.app.presentation.bookings.events_logic.get_event") as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.events_logic.assert_user_is_organizer"
#         ) as mock_assert_organizer,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.get_event_participants"
#         ) as mock_get_event_participants,
#     ):
#         response = client.get("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_not_called()
#     mock_assert_organizer.assert_not_called()
#     mock_get_event_participants.assert_not_called()
#     assert response.status_code == HTTP_401_UNAUTHORIZED


# def test__get_event_participants__no_event() -> None:
#     """Test to get the list of event's participants."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     with (
#         patch("src.app.presentation.bookings.user_logic.get_user") as mock_get_user,
#         patch(
#             "src.app.presentation.bookings.events_logic.get_event",
#             side_effect=event_errors.EventNotFoundError(1),
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.events_logic.assert_user_is_organizer"
#         ) as mock_assert_organizer,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.get_event_participants"
#         ) as mock_get_event_participants,
#     ):
#         response = client.get("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_called_once_with(1, mock_db)
#     mock_assert_organizer.assert_not_called()
#     mock_get_event_participants.assert_not_called()
#     assert response.status_code == HTTP_400_BAD_REQUEST


# def test__get_event_participants__not_oranizatior() -> None:
#     """Test to get the list of event's participants from non-organizer."""
#     mock_db = MagicMock()
#     app.dependency_overrides[get_db] = lambda: mock_db
#     app.dependency_overrides[get_current_user] = lambda: "g.popov@inno.ru"

#     mock_user = create_mock_user()
#     mock_event = create_mock_event()

#     with (
#         patch(
#             "src.app.presentation.bookings.user_logic.get_user", return_value=mock_user
#         ) as mock_get_user,
#         patch(
#             "src.app.presentation.bookings.events_logic.get_event",
#             return_value=mock_event,
#         ) as mock_get_event,
#         patch(
#             "src.app.presentation.bookings.events_logic.assert_user_is_organizer",
#             side_effect=event_errors.OrginizatorRoleRequiredError(1, "g.popov@inno.ru"),
#         ) as mock_assert_organizer,
#         patch(
#             "src.app.presentation.bookings.bookings_logic.get_event_participants"
#         ) as mock_get_event_participants,
#     ):
#         response = client.get("/bookings/1")

#     mock_get_user.assert_called_once_with("g.popov@inno.ru", mock_db)
#     mock_get_event.assert_called_once_with(1, mock_db)
#     mock_assert_organizer.assert_called_once_with(mock_event, mock_user)
#     mock_get_event_participants.assert_not_called()
#     assert response.status_code == HTTP_403_FORBIDDEN
