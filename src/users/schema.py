from pydantic import BaseModel, Field

class UserBase(BaseModel):
  email: str
  password: str


class UserCreate(UserBase):
  name: str


class UserSchema(UserBase):
  id: int
  name: str
  password:str = Field(exclude=True)

  class Config:
    from_attributes = True

class Token(BaseModel):
  access_token: str
  token_type: str

class TokenData(BaseModel):
  email: str | None = None