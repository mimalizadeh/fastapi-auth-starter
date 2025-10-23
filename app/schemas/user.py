from pydantic import BaseModel, ConfigDict, Field


class UserSchemaIn(BaseModel):
    """This model use for get signup data"""
    username: str = Field(default="admin")
    email: str = Field(default="admin@mail.com")
    first_name: str = Field(default="admin")
    last_name: str = Field(default="admin")
    password: str = Field(default="admin")


class UserSchema(BaseModel):
    """This model use for send user profile data"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    first_name: str
    last_name: str
