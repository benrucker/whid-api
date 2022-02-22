from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class TestMainWithAuth:
    client = TestClient(app)
    auth = {"Authorization": f"Bearer hello"}

    def test_read_main(self):
        response = self.client.get(
            "/",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

    def test_message(self):
        response = self.client.get(
            "/message/1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.client.put(
            "/message/1",
            headers=self.auth,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello",
                "author": 1,
                "channel": 1,
            },
        )
        assert response.status_code == 200

        response = self.client.get(
            "/message/1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['id'] == 1
        assert response.json()['timestamp'] == "2020-01-01T00:00:00"
        assert response.json()['content'] == 'hello'
        assert response.json()['author'] == 1

    def test_user(self):
        response = self.client.get(
            "/user/1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.client.put(
            "/user/1",
            headers=self.auth,
            json={
                "id": 1,
                "username": "test",
                "nickname": "testname",
                "numbers": 8098,
            }
        )
        assert response.status_code == 200

        response = self.client.get(
            "/user/1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['id'] == 1
        assert response.json()['username'] == 'test'
        assert response.json()['nickname'] == 'testname'
        assert response.json()['numbers'] == 8098

    def test_channel(self):
        response = self.client.get(
            "/channel/1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.client.put(
            "/channel/1",
            headers=self.auth,
            json={
                "id": 1,
                "name": "channel",
                "category": "general",
                "thread": False,
            }
        )
        assert response.status_code == 200

        response = self.client.get(
            "/channel/1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['id'] == 1
        assert response.json()['name'] == 'channel'
        assert response.json()['category'] == 'general'
        assert response.json()['thread'] == False
