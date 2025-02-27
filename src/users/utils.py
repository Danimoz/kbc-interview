import jwt
from datetime import timedelta, datetime, timezone
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from src.users.model import User
from src.core.config import settings
from src.users.schema import UserCreate, UserSchema, UserBase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
  return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)


async def create_user(db: AsyncSession, user: UserCreate) -> UserSchema:
  hashed_password = get_password_hash(user.password)
  db_user = User(name=user.name, email=user.email, password=hashed_password)
  db.add(db_user)
  await db.commit()
  await db.refresh(db_user)
  return db_user

async def get_user_by_email(db: AsyncSession, email: str) -> User:
  result = await db.execute(select(User).where(User.email == email))
  return result.scalars().first()

async def authenticate_user(db: AsyncSession, user: UserBase):
  user_in_db = await get_user_by_email(db, user.email)
  print(user_in_db)
  if not user_in_db:
    return False
  if not verify_password(user.password, user_in_db.password):
    return False
  return user_in_db

def create_access_token(data: dict, expires_delta: timedelta | None = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
  to_encode.update({ 'exp': expire })
  encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.HASH_ALGORITHM)
  return encoded_jwt


def decode_jwt(token: str) -> dict:
  try:
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.HASH_ALGORITHM])
    exp_timestamp = decoded_token.get("exp")
    if exp_timestamp:
      exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
      if datetime.now(timezone.utc) >= exp_datetime:
        raise jwt.ExpiredSignatureError
    return decoded_token
  except jwt.ExpiredSignatureError:
    print("Token has expired")
    return None
  except jwt.InvalidTokenError as e:
    print("Invalid Token:", str(e))
    return None
  except Exception as e:
    print(f"Unexpected error: {e}")
    return None



class JWTBearer(HTTPBearer):
  def __init__(self, auto_error: bool = True):
    super(JWTBearer, self).__init__(auto_error=auto_error)

  async def __call__(self, request: Request):
    credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
    if credentials:
      print(f"Credentials: {credentials}")
      if not credentials.scheme == "Bearer":
        raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
      if not self.verify_jwt(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
      return credentials.credentials
    else:
      raise HTTPException(status_code=403, detail="Invalid authorization code.")

  def verify_jwt(self, jwtoken: str) -> bool:
    isTokenValid: bool = False
    try:
      payload = decode_jwt(jwtoken)
    except:
      payload = None
    if payload:
      isTokenValid = True

    return isTokenValid