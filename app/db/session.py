from .setup import create_async_engine, create_session_pool
from app.core.config import get_settings, logger

settings = get_settings()

engine = create_async_engine(url=settings.database_url)
SessionPool = create_session_pool(engine)


async def get_session_pool():
    async with SessionPool() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.exception(f"DB session rollback due to: {e}", exc_info=True)
            raise
        finally:
            await session.close()
