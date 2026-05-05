from db.models import Base
from db.session import get_engine


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)


def drop_db():
    engine = get_engine()
    Base.metadata.drop_all(engine)


def reset_db():
    drop_db()
    init_db()