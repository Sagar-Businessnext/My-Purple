# OWASP Mitigations — Library and Middleware Reference

## FastAPI Security Middleware Stack

A production FastAPI application should register these middleware components in order:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from my_service.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title="My Service",
        # Do not expose error details in production
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
    )

    # 1. Trusted host (prevents host header injection)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

    # 2. CORS (explicit origins only)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # 3. Rate limiting
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    return app
```

## Authentication Pattern (JWT)

```python
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    payload = {"sub": str(subject), "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserContext:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[ALGORITHM],  # explicit whitelist prevents alg:none attack
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return UserContext(user_id=int(user_id))
```

## Input Validation with Pydantic

Pydantic v2 validates on parse. Combine with explicit field constraints to prevent injection at the schema boundary.

```python
from pydantic import BaseModel, Field, field_validator
import re

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    page: int = Field(default=1, ge=1, le=1000)
    page_size: int = Field(default=20, ge=1, le=100)

    @field_validator("query")
    @classmethod
    def no_sql_keywords(cls, v: str) -> str:
        # Additional layer — parameterized queries are the primary defense
        blocked = re.compile(r"\b(DROP|DELETE|INSERT|UPDATE|UNION|SELECT)\b", re.IGNORECASE)
        if blocked.search(v):
            raise ValueError("Query contains disallowed keywords")
        return v
```

## Safe Deserialization

| Format | Safe | Unsafe |
|--------|------|--------|
| JSON | `json.loads()` always safe | — |
| YAML | `yaml.safe_load()` | `yaml.load()` (executes Python tags) |
| Pickle | Never safe for external data | `pickle.loads()` always a risk |
| msgpack | `msgpack.unpackb(raw, raw=False)` | Unpacking untrusted bytes with `object_hook` |

```python
# For inter-service messaging, use JSON or msgpack — never pickle
import json

def deserialize_event(raw_bytes: bytes) -> dict:
    return json.loads(raw_bytes)
```

## Secrets Management

```python
# WRONG — hardcoded secret
DATABASE_URL = "postgresql://user:hardcoded_password@db/mydb"

# CORRECT — pydantic-settings reads from environment
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    jwt_secret: str
    allowed_origins: list[str] = ["https://app.businessnext.com"]
    allowed_hosts: list[str] = ["api.businessnext.com"]
    debug: bool = False

settings = Settings()
```

Never log `settings.jwt_secret`, `settings.database_url`, or any secret value.
