import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.schema import UserCreate, UserSchema, Token, UserBase, TokenData
from src.users.utils import create_user, get_user_by_email, authenticate_user, create_access_token 
from src.core.db import get_db
from src.core.config import settings

router = APIRouter(
  prefix="/users", 
  tags=["users"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserSchema:
  existing_user = await get_user_by_email(db, user.email)
  if existing_user:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="User with this email already exists."
    )
  return await create_user(db=db, user=user)


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user: UserBase, db: AsyncSession = Depends(get_db)):
  existing_user = await authenticate_user(db, user)
  if not existing_user:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Incorect username or Password",
      headers={"WWW-Authenticate": "Bearer"}
    )
  acceess_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token(data={"sub": existing_user.email}, expires_delta=acceess_token_expires)
  return Token(access_token=access_token, token_type="bearer")


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.HASH_ALGORITHM])
    email: str = payload.get("sub")
    if email is None:
      raise credentials_exception
    token_data = TokenData(email=email)
  except InvalidTokenError:
    raise credentials_exception
  
  user = await get_user_by_email(db, token_data.email)
  if user is None:
    raise credentials_exception
  return user