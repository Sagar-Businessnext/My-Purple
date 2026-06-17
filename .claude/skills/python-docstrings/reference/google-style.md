# Google-Style Docstrings Reference

## Module Docstring

```python
"""User service — business logic for user lifecycle management.

This module provides the UserService class, which handles user creation,
authentication, profile updates, and deactivation. It delegates database
access to UserRepository and sends notifications via the notification client.
"""
```

## Function Docstring

```python
async def create_user(
    email: str,
    full_name: str,
    role: str = "viewer",
) -> User:
    """Create a new user account and send a welcome email.

    Validates that the email is not already registered, creates the user
    record, and dispatches a welcome notification asynchronously.

    Args:
        email: The email address for the new account. Must be unique.
        full_name: The user's display name. Stored as provided; not normalized.
        role: The initial access role. Defaults to ``"viewer"``.

    Returns:
        The newly created User instance with the generated ``id`` populated.

    Raises:
        DuplicateEmailError: If a user with the given email already exists.
        ValueError: If ``email`` is empty or not a valid email format.

    Example:
        >>> user = await create_user("alice@example.com", "Alice Smith")
        >>> user.role
        'viewer'
    """
```

## Class Docstring

```python
class UserService:
    """Handles all user lifecycle operations for the application.

    This service is the single point of entry for creating, updating,
    retrieving, and deactivating users. It owns the business rules around
    user management and delegates I/O to UserRepository.

    Attributes:
        repo: The repository used for database access.
        notifier: The notification client for sending emails and in-app alerts.

    Example:
        >>> service = UserService(repo=UserRepository(db), notifier=EmailNotifier())
        >>> user = await service.get_by_id(42)
    """

    def __init__(self, repo: UserRepository, notifier: NotificationClient) -> None:
        """Initialize UserService with its required dependencies.

        Args:
            repo: Repository for user database operations.
            notifier: Client for dispatching user notifications.
        """
        self.repo = repo
        self.notifier = notifier
```

## Property Docstring

```python
@property
def is_active(self) -> bool:
    """Whether the user account is currently active and can authenticate."""
    return self._is_active
```

## Exception Class Docstring

```python
class UserNotFoundError(ValueError):
    """Raised when a user lookup by ID or email returns no result.

    This exception signals to the caller that the resource does not exist,
    and the appropriate HTTP response is 404 Not Found.

    Attributes:
        user_id: The ID that was not found, if provided.
        email: The email that was not found, if provided.
    """

    def __init__(self, user_id: int | None = None, email: str | None = None) -> None:
        """Initialize with the identifier that failed the lookup.

        Args:
            user_id: The numeric user ID that was not found.
            email: The email address that was not found.
        """
        self.user_id = user_id
        self.email = email
        identifier = f"id={user_id}" if user_id else f"email={email}"
        super().__init__(f"User not found: {identifier}")
```

## Generator Function Docstring

```python
async def stream_active_users() -> AsyncGenerator[User, None]:
    """Yield all active users in the database one at a time.

    Uses a server-side cursor to avoid loading all users into memory.
    Suitable for bulk export or background processing tasks.

    Yields:
        User instances with ``is_active=True``, ordered by creation date.

    Example:
        >>> async for user in stream_active_users():
        ...     await process(user)
    """
```

## Sections Reference

| Section | Required When | Notes |
|---------|--------------|-------|
| Summary line | Always | One sentence, imperative mood |
| Extended description | When needed | Extra context not obvious from the signature |
| `Args:` | Any parameters present | One sub-item per parameter; type omitted (in annotation) |
| `Returns:` | Non-None return | Describe the value; omit for `-> None` |
| `Yields:` | Generator function | Use instead of `Returns:` |
| `Raises:` | Any exception raised | All domain and validation exceptions |
| `Attributes:` | Class docstring only | Public instance/class attributes |
| `Example:` | Public non-trivial API | Must be syntactically correct |

## Inline Formatting

- Use double backticks for code: `` ``user_id`` ``, `` ``None`` ``
- Use single backticks for references that Sphinx links: `:class:`UserService``
- Do not use Markdown bold (`**`) in docstrings — not rendered by Sphinx
