from pydantic import BaseModel, ConfigDict
import pytest
from httpx import Headers

from app.tests.conftest import logger
import os

os.environ["ENV"] = "test"

root_api_path = "/api/v1"


class CookieSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')
    access_token: str = None
    refresh_token: str = None
    token_type: str = "cookie"


class AuthState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cookies: CookieSchema = CookieSchema()
    headers: Headers = None


@pytest.fixture(scope="session")
def auth_state() -> AuthState:
    """Shared state between tests"""
    return AuthState()

@pytest.fixture(scope="session")
def signup_data(client):
    """
    Provides consistent user data for signup
    """

    data = {
        "username": "admin",
        "email": "admin@mail.com",
        "first_name": "admin",
        "last_name": "admin",
        "password": "admin"
    }
    return data


@pytest.fixture(scope="session")
def signin(client, signup_data, auth_state):
    """
    Test signin function : this fixture signup new user and then login them and return Response

    :param client: httpx client
    :param signup_data: user data for signup
    :param auth_state: user state
    :return: httpx response
    """
    # Preform signup
    response = client.post(f"{root_api_path}/auth/signup", json=signup_data)
    assert response.status_code == 200

    # Preform signin
    data = {
        "username": signup_data.get("email"),
        "password": signup_data.get("password"),
    }

    response = client.post(f'{root_api_path}/auth/signin', json=data)
    assert response.status_code == 200


    auth_state.cookies = CookieSchema(**response.cookies)
    auth_state.headers = response.headers
    logger.info(f"signin successful : {auth_state.cookies.model_dump()}")
    return True


@pytest.fixture(scope="function")
def get_me(client, auth_state):
    """
    Test get me function : after create user and login get user data

    :param client: httpx client
    :param auth_state: user state
    :return:
    """
    cookies = auth_state.cookies.model_dump(mode="json")

    response = client.get(f"{root_api_path}/users/me", cookies=cookies, headers=auth_state.headers)
    assert response.status_code == 200

    data = response.json()
    logger.info(f"Response data: {data}")

    assert "username" in data
    assert "hashed_password" not in data

    return True


@pytest.mark.dependency(name="test_01_create_user")
def test_01_create_user(signin):
    """Create user and save authentication data """
    assert signin is True


@pytest.mark.dependency(name="test_02_pre_refresh_get_me", depends=["test_01_create_user"])
def test_02_pre_refresh_get_me(get_me):
    """Run fixture(function) get me"""
    assert get_me is True


@pytest.mark.dependency(name="test_03_refresh_token", depends=["test_02_pre_refresh_get_me"])
def test_03_refresh_token(client, auth_state):
    """refresh access token if refresh token is valid"""
    auth_state.cookies.access_token = None
    cookies = auth_state.cookies.model_dump(mode="json", exclude={"cookies": {"refresh_token"}})
    response = client.post(f"{root_api_path}/auth/refresh", cookies=cookies)

    assert response.status_code == 200
    auth_state.cookies = CookieSchema(**response.cookies)

    data = response.json()
    logger.info(f"Access token successfully refreshed and state updated : {data}")


@pytest.mark.dependency(name="test_04_after_refresh_get_me", depends=["test_03_refresh_token"])
def test_04_after_refresh_get_me(get_me):
    """Run fixture(function) get me"""
    assert get_me is True


@pytest.mark.dependency(name="test_05_logout", depends=["test_04_after_refresh_get_me"])
def test_05_logout(client, auth_state):
    """Logout user and delete all authentication data"""
    cookies = auth_state.cookies.model_dump(mode="json")
    response = client.post(f"{root_api_path}/auth/logout", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    auth_state.cookies = CookieSchema()
    auth_state.headers = None
    logger.info(f"Logout successfully refreshed and state updated : {data}")


@pytest.mark.dependency(name="test_06_after_log_get_me", depends=["test_05_logout"])
def test_06_get_me_unauthorized(client, auth_state):
    """chek user is logged out"""
    response = client.get(f"{root_api_path}/users/me", cookies=auth_state.cookies.model_dump())
    assert response.status_code == 401
