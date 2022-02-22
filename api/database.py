import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _declarative_base_auto_instantiate_nested(self, **kwargs):
    cls_ = type(self)
    relationships = self.__mapper__.relationships

    for k in kwargs:
        if not hasattr(cls_, k):
            raise TypeError(
                "%r is an invalid keyword argument for %s" % (k, cls_.__name__)
            )
        if k in relationships.keys():
            if relationships[k].direction.name == 'ONETOMANY':
                childclass = getattr(
                    sys.modules[self.__module__], relationships[k].argument)
                setattr(self, k, [childclass(**elem) for elem in kwargs[k]])
        else:
            setattr(self, k, kwargs[k])


_declarative_base_auto_instantiate_nested.__name__ = "__init__"


Base = declarative_base(constructor=_declarative_base_auto_instantiate_nested)
