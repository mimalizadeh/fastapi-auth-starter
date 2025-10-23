# Fastapi Auth Starter

### A simple structure for validation and authentication with access token and refresh token for FastAPI

# How to use 
____

1. #### Clone project
2. #### Create `.env` file from `.env.example` :
       $ cp .env .env.example
3. #### Create virtualenv
       $ virtualenv -p python3 fas-venv
4. #### Install requirements
       $ pip install -r requirements.txt
5. #### Create docker containers
       $ docker compose up -d --build
6. #### Create models with alembic :
       $ alembic revision --autogenerat -m "init"
       $ alembic upgrade head
7. #### Test with pytest
       $ pytest
8. #### You can see project docs in url :
        http://localhost:8000/api/docs

# Features
___

* ✅ | Users can sign up user with `Email` ,`Username`, `Firstname` , `Lastname` , `password` 
* ✅ | Validation and authentication with token , cookie based
* ❌ | Query count limiter with `Redis` 