from typing import Annotated

from fastapi import Depends
from app.db.session import get_session_pool
from app.db.repo.request import RequestRepo


def get_request_repo(session=Depends(get_session_pool)):
    """
    Create request repository and return it as Annotated
    """
    return RequestRepo(session)


RepoRequestDep = Annotated[RequestRepo, Depends(get_request_repo)]
