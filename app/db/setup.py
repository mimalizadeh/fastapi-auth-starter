from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


def create_engine(data_base_url: str, echo=False):
    """ Create engine
     :param data_base_url: database url
     :param echo: boolean
     :return: engine
     """
    engine = create_async_engine(
        url=data_base_url,
        echo=echo,
        query_cache_size=1200,
        pool_size=20,
        max_overflow=200,
        future=True
    )
    return engine


def create_session_pool(engin) -> AsyncSession:
    """ Create session pool
    :param engin: Engine instance
    :return: session pool
    """
    session_pool = async_sessionmaker(
        engin, class_=AsyncSession, expire_on_commit=False
    )

    return session_pool
