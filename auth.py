# auth.py

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import string
import secrets

import os


# --- 1. PASSWORD HASHING ---

# This tells passlib to use the "bcrypt" algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """Hashes a plain-text password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Checks if a plain-text password matches a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)


# --- 2. JWT (TOKEN) CREATION & VALIDATION ---

# A secret key to sign our tokens.
# IMPORTANT: In a real app, this MUST be a complex, random string
# and should NOT be written directly in the code.
# You would load it from an environment variable.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set in .env file")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # A token will last for 30 minutes

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Give it a default expiration time
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# We won't need this in Step 1, but we'll need it later to verify 
# the token on our calendar page.
def verify_access_token(token: str):
    """Checks a token's validity and returns the payload (data)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None # Token is invalid or expired


def generate_company_code(length: int = 6):
    """Generates a random, 6-character, uppercase alphanumeric code."""
    # Create a pool of characters (e.g., ABCDE...12345)
    alphabet = string.ascii_uppercase + string.digits
    # Pick 6 random characters from the pool
    return ''.join(secrets.choice(alphabet) for i in range(length))