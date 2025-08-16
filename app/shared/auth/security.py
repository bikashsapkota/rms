from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def decode_access_token(token: str) -> Optional[str]:
    """Decode JWT token and return subject."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject: str = payload.get("sub")
        if subject is None:
            return None
        return subject
    except JWTError:
        return None


def create_token_payload(
    user_id: str,
    email: str,
    organization_id: str,
    restaurant_id: Optional[str] = None,
    role: str = "staff"
) -> Dict[str, Any]:
    """Create JWT token payload with user context."""
    return {
        "user_id": user_id,
        "email": email,
        "organization_id": organization_id,
        "restaurant_id": restaurant_id,
        "role": role,
        "iat": datetime.utcnow(),
    }


def create_user_access_token(
    user_id: str,
    email: str,
    organization_id: str,
    restaurant_id: Optional[str] = None,
    role: str = "staff",
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create access token with user context."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = create_token_payload(user_id, email, organization_id, restaurant_id, role)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_user_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode user JWT token and return payload."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None