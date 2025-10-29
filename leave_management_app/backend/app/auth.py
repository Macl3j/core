"""Authentication utilities and JWT token management."""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .schemas import TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    print(f"[AUTH] Creating JWT with data: {to_encode}")
    print(f"[AUTH] Using SECRET_KEY: {SECRET_KEY[:10]}...")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"[AUTH] Generated JWT token: {encoded_jwt[:50]}...")
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        username: str = payload.get("username")
        print(f"[AUTH] JWT payload: sub={user_id_str}, username={username}")

        # Convert sub from string to int
        if user_id_str is None:
            print("[AUTH] JWT decode failed - user_id is None")
            return None

        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError) as e:
            print(f"[AUTH] JWT decode failed - cannot convert sub to int: {e}")
            return None

        return TokenData(user_id=user_id, username=username)
    except JWTError as e:
        print(f"[AUTH] JWT decode error: {str(e)}")
        return None


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    print(f"[AUTH] Received token: {token[:50]}..." if len(token) > 50 else f"[AUTH] Received token: {token}")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_access_token(token)
    print(f"[AUTH] Decoded token data: {token_data}")

    if token_data is None or token_data.user_id is None:
        print("[AUTH] Token validation failed - invalid token data")
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        print(f"[AUTH] User not found for ID: {token_data.user_id}")
        raise credentials_exception

    if not user.is_active:
        print(f"[AUTH] User {user.username} is inactive")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    print(f"[AUTH] Successfully authenticated user: {user.username}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(*allowed_roles: str):
    """Dependency to require specific user roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker
