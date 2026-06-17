# pytest Parametrize Recipes Reference

## Basic Parametrize

```python
import pytest

@pytest.mark.parametrize("amount,currency,expected", [
    (100, "USD", "$1.00"),
    (0,   "USD", "$0.00"),
    (999, "EUR", "€9.99"),
])
def test_format_money(amount: int, currency: str, expected: str) -> None:
    result = format_money(amount, currency)
    assert result == expected
```

## Parametrize with Explicit IDs

Without IDs, pytest generates `test_validate_email[value0]`, `test_validate_email[value1]`. Explicit IDs make failures readable.

```python
@pytest.mark.parametrize("email,is_valid", [
    pytest.param("user@example.com", True,  id="valid-standard"),
    pytest.param("user+tag@example.com", True, id="valid-with-plus"),
    pytest.param("@example.com",     False, id="missing-local-part"),
    pytest.param("user@",            False, id="missing-domain"),
    pytest.param("",                 False, id="empty-string"),
    pytest.param("not-an-email",     False, id="no-at-sign"),
], ids=str)  # or omit ids= and use pytest.param(..., id=...) per case
def test_validate_email(email: str, is_valid: bool) -> None:
    assert validate_email(email) == is_valid
```

## Parametrize Error Paths

```python
@pytest.mark.parametrize("input_data,expected_error", [
    ({"amount": -1},    ValueError),
    ({"amount": None},  TypeError),
    ({"amount": "abc"}, TypeError),
])
def test_create_order_rejects_invalid_amount(
    input_data: dict,
    expected_error: type[Exception],
) -> None:
    with pytest.raises(expected_error):
        create_order(**input_data)
```

## Matrix Parametrize (Two Axes)

```python
@pytest.mark.parametrize("role", ["admin", "manager", "viewer"])
@pytest.mark.parametrize("resource", ["users", "orders", "reports"])
def test_permission_check_covers_all_combinations(role: str, resource: str) -> None:
    result = has_read_permission(role=role, resource=resource)
    assert isinstance(result, bool)  # just ensure it doesn't raise
```

## Indirect Fixtures with Parametrize

Use `indirect=True` when the parametrize value should be passed to a fixture rather than directly to the test.

```python
@pytest.fixture
def user_with_role(request) -> User:
    """Creates a user with the role specified via indirect parametrize."""
    return User(id=1, email="test@example.com", role=request.param)


@pytest.mark.parametrize("user_with_role", ["admin", "manager"], indirect=True)
def test_privileged_users_can_access_audit_log(user_with_role: User) -> None:
    assert can_access_audit_log(user_with_role) is True


@pytest.mark.parametrize("user_with_role", ["viewer", "guest"], indirect=True)
def test_unprivileged_users_cannot_access_audit_log(user_with_role: User) -> None:
    assert can_access_audit_log(user_with_role) is False
```

## Marking Specific Parametrize Cases

```python
@pytest.mark.parametrize("n,expected", [
    (0, 0),
    (1, 1),
    (10, 55),
    pytest.param(1000, 43466557686937456435688527675040625802564660517371780402481729089536555417949051890403879840079255169295922593080322634775209689623239873322471161642996440906533187938298969649928516003704476137795166849228875, id="large-n", marks=pytest.mark.slow),
])
def test_fibonacci(n: int, expected: int) -> None:
    assert fibonacci(n) == expected
```

## Avoiding Common Parametrize Mistakes

```python
# WRONG — parametrize over booleans usually means two separate tests
@pytest.mark.parametrize("is_active", [True, False])
def test_user_status(is_active: bool) -> None:
    user = User(is_active=is_active)
    # what exactly are we testing?

# BETTER — name the behaviors explicitly
def test_active_user_can_login() -> None:
    user = User(is_active=True)
    assert user.can_login() is True

def test_inactive_user_cannot_login() -> None:
    user = User(is_active=False)
    assert user.can_login() is False
```
