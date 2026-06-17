# OWASP Top 10 — Python Mapping

## A01: Broken Access Control

**Python vector:** Missing authorization checks in route handlers; relying on the frontend to hide restricted links.

```python
# WRONG — any authenticated user can access any user's data
@router.get("/users/{user_id}/profile")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    return await user_repo.get(user_id)  # no ownership check

# CORRECT — verify the requester owns or has permission to view the resource
@router.get("/users/{user_id}/profile")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return await user_repo.get(user_id)
```

## A02: Cryptographic Failures

**Python vector:** Using `hashlib.md5` or `hashlib.sha1` for password storage; storing secrets in plain text env vars without rotation.

```python
# WRONG — MD5 is broken for passwords
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()

# CORRECT — use bcrypt or argon2 via passlib
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(password)
is_valid = pwd_context.verify(plain_password, hashed)
```

## A03: Injection

**Python vector:** String-formatted SQL queries; `os.system()` with user input; Jinja2 with `autoescape=False`.

```python
# WRONG — SQL injection via f-string
query = f"SELECT * FROM users WHERE email = '{user_email}'"
result = await db.execute(text(query))

# CORRECT — parameterized query via SQLAlchemy
from sqlalchemy import select, text
result = await db.execute(
    select(User).where(User.email == user_email)
)
# Or with raw SQL:
result = await db.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": user_email},
)
```

## A04: Insecure Design

**Python vector:** Missing rate limiting on authentication endpoints; no account lockout after failed attempts.

```python
# CORRECT — use slowapi for FastAPI rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    ...
```

## A05: Security Misconfiguration

**Python vector:** `DEBUG = True` in production; CORS wildcard `*`; stack traces exposed in API responses.

```python
# WRONG — CORS wildcard exposes all origins
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)

# CORRECT — explicit origin whitelist
from my_service.config import settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # ["https://app.businessnext.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## A06: Vulnerable and Outdated Components

**Python vector:** Dependencies with known CVEs; unpinned `requirements.txt`.

```
# CHECK: run pip-audit
pip-audit

# CHECK: outdated packages
pip list --outdated
```

Pin exact versions in `requirements.txt`; use version ranges with upper bounds in `pyproject.toml`.

## A07: Identification and Authentication Failures

**Python vector:** JWT decoded without algorithm whitelisting; accepting `alg: none`; weak secrets.

```python
# WRONG — no algorithm constraint
payload = jwt.decode(token, key)

# CORRECT — whitelist the algorithm
from jose import jwt, JWTError
ALGORITHM = "HS256"
try:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
except JWTError:
    raise HTTPException(status_code=401, detail="Invalid token")
```

## A08: Software and Data Integrity Failures

**Python vector:** `pickle.loads()` on untrusted data; unsafe `yaml.load()`.

```python
# WRONG — pickle deserializes arbitrary code
import pickle
data = pickle.loads(user_provided_bytes)  # CRITICAL vulnerability

# WRONG — yaml.load with default loader executes Python objects
import yaml
data = yaml.load(user_provided_string)

# CORRECT — use safe alternatives
import json
data = json.loads(user_provided_bytes)  # json is always safe for structured data

import yaml
data = yaml.safe_load(user_provided_string)  # safe loader only
```

## A09: Security Logging and Monitoring Failures

**Python vector:** Not logging failed authentication attempts; logging sensitive data (passwords, tokens).

```python
# CORRECT — log security events without sensitive data
import logging
logger = logging.getLogger(__name__)

async def authenticate(credentials: LoginRequest) -> User | None:
    user = await user_repo.find_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(
            "Failed login attempt for email=%s from ip=%s",
            credentials.email,
            request.client.host,  # not logging the password
        )
        return None
    logger.info("Successful login for user_id=%s", user.id)
    return user
```

## A10: Server-Side Request Forgery (SSRF)

**Python vector:** User-controlled URL passed directly to `httpx.get()` or `requests.get()`.

```python
# WRONG — allows attacker to probe internal services
@router.get("/fetch")
async def fetch_url(url: str):
    async with httpx.AsyncClient() as client:
        return await client.get(url)  # url = "http://169.254.169.254/latest/meta-data/"

# CORRECT — validate against an allowlist
ALLOWED_HOSTS = {"api.partner.com", "feeds.partner.com"}

@router.get("/fetch")
async def fetch_url(url: str):
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_HOSTS:
        raise HTTPException(status_code=400, detail="URL not in allowlist")
    async with httpx.AsyncClient() as client:
        return await client.get(url)
```
