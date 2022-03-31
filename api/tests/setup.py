from datetime import date, datetime
import pytest
import sqlalchemy
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api import schemas

from ..database import Base
from ..main import app, get_db, token
from ..settings import get_settings


SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@sqlalchemy.event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # disable pysqlite's emitting of the BEGIN statement entirely.
    # also stops it from emitting COMMIT before any DDL.
    dbapi_connection.isolation_level = None


@sqlalchemy.event.listens_for(engine, "begin")
def do_begin(conn):
    # emit our own BEGIN
    conn.exec_driver_sql("BEGIN")


@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    session.add(schemas.Epoch(id=1, start=date(2022, 1, 1), end=date(2022, 3, 31)))
    session.add(schemas.Epoch(id=2, start=date(2022, 4, 1), end=date(2022, 4, 7)))
    session.add(schemas.Epoch(id=3, start=date(2022, 4, 8), end=date(2022, 4, 14)))
    session.add(schemas.Epoch(id=4, start=date(2022, 4, 15), end=date(2022, 4, 21)))
    session.commit()

    # Begin a nested transaction (using SAVEPOINT).
    nested = connection.begin_nested()

    # If the application code calls session.commit, it will end the nested
    # transaction. Need to start a new one when that happens.
    @sqlalchemy.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]
