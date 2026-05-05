from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from config import DATABASE_PATH
import threading

_engine = None
_session_factory = None
_lock = threading.local()


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine())
    return _session_factory


def get_session() -> Session:
    if not hasattr(_lock, "session") or _lock.session is None:
        factory = get_session_factory()
        _lock.session = factory()
    return _lock.session


def close_session():
    if hasattr(_lock, "session") and _lock.session is not None:
        _lock.session.close()
        _lock.session = None


def commit_with_retry(session: Session, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            if attempt == max_retries - 1:
                raise e
    return False