from pydantic import BaseModel, Field


class TokenSchema(BaseModel):
    """This model use for send auth tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "cookie"


class LoginSchema(BaseModel):
    """This model use for get login data"""
    username: str = Field(description="Username", default="admin@mail.com")
    password: str = Field(description="password", default="admin")
