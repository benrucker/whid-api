from fastapi.testclient import TestClient

from ..database import Base
from ..main import app, get_db, token
from .setup import client, session


class TestMisc:
    client = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    def test_main(self):
        response = self.client.get(
            "/",
            headers=self.auth
        )
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

class TestMessages:
    client = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    def test_message(self, client):
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
        assert response.json()['channel'] == 1
        assert response.json()['edited'] == False
        assert response.json()['edited_timestamp'] == None
        assert response.json()['deleted'] == False
        assert response.json()['pinned'] == False

    def test_message_with_attachments(self, client):
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
                "attachments": [
                    {
                        "msg_id": 1,
                        "url": "https://example.com/image.png",
                    },
                    {
                        "msg_id": 1,
                        "url": "https://example.com/image2.png",
                    },
                ],
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
        assert response.json()['channel'] == 1
        assert response.json()['edited'] == False
        assert response.json()['edited_timestamp'] == None
        assert response.json()['deleted'] == False
        assert response.json()['pinned'] == False
        assert response.json()['attachments'] == [
            {
                "msg_id": 1,
                "url": "https://example.com/image.png",
            },
            {
                "msg_id": 1,
                "url": "https://example.com/image2.png",
            },
        ]

    def test_update_nonexistant_message(self, client):
        response = self.client.patch(
            "/message/1",
            headers=self.auth,
            json={
                "content": "new content",
                "edited": True,
                "edited_timestamp": "2020-01-01T00:00:00",
            },
        )
        assert response.status_code == 404

    def test_update_message(self, client):
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

        response = self.client.patch(
            "/message/1",
            headers=self.auth,
            json={
                "content": "new content",
                "edited": True,
                "edited_timestamp": "2020-01-01T00:00:00",
            },
        )
        assert response.status_code == 200
        assert response.json()['content'] == 'new content'
        assert response.json()['edited'] == True
        assert response.json()['edited_timestamp'] == '2020-01-01T00:00:00'

        response = self.client.put(
            "/pin/1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['pinned'] == True
        
        response = self.client.patch(
            "/message/1",
            headers=self.auth,
            json={
                "deleted": True,
            },
        )
        assert response.status_code == 200
        assert response.json()['deleted'] == True

    def test_delete_message(self, client):
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

        response = self.client.delete(
            "/message/1",
            headers=self.auth,
        )
        assert response.status_code == 200

        response = self.client.get(
            "/message/1",
            headers=self.auth,
        )
        assert response.status_code == 404

class TestChannels:
    client = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    def test_channel(self, client):
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

    def test_update_nonexistant_channel(self, client):
        response = self.client.patch(
            "/channel/1",
            headers=self.auth,
            json={
                "name": "new name",
            },
        )
        assert response.status_code == 404

    def test_update_channel(self, client):
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
        assert response.json()['name'] != 'new channel'
        assert response.json()['category'] != 'general2'

        response = self.client.patch(
            "/channel/1",
            headers=self.auth,
            json={
                "name": "new channel",
                "category": "general2",
            }
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'new channel'
        assert response.json()['category'] == 'general2'

class TestUsers():
    client = TestClient(app)
    auth = {"Authorization": "Bearer hello"}


    def test_user(self, client):
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

    def test_update_nonexistant_user(self, client):
        response = self.client.patch(
            "/user/1",
            headers=self.auth,
            json={
                "username": "new name",
            },
        )
        assert response.status_code == 404

    def test_update_user(self, client):
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
        assert response.json()['username'] == 'test'
        assert response.json()['nickname'] == 'testname'
        assert response.json()['username'] != 'new username'
        assert response.json()['nickname'] != 'new nickname'
        assert response.json()['numbers'] == 8098

        response = self.client.patch(
            "/user/1",
            headers=self.auth,
            json={
                "username": "new username",
                "nickname": "new nickname",
            }
        )
        assert response.status_code == 200
        assert response.json()['username'] == 'new username'
        assert response.json()['nickname'] == 'new nickname'
        assert response.json()['numbers'] == 8098


class TestEvents:
    client = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    def test_voice_event(self, client):
        response = self.client.get(
            "/voice_event?since=2020-01-01T00:00:00&user=1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.client.post(
            "/voice_event",
            headers=self.auth,
            json={
                "user_id": 1,
                "type": "join",
                "channel": 1,
                "timestamp": "2020-01-01T00:00:00",
            }
        )
        assert response.status_code == 200

        response = self.client.get(
            "/voice_event?since=2020-01-01T00:00:00&user=1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['user_id'] == 1
        assert response.json()[0]['type'] == 'join'
        assert response.json()[0]['channel'] == 1
        assert response.json()[0]['timestamp'] == '2020-01-01T00:00:00'

        # fail when all events are in past
        response = self.client.get(
            "/voice_event?since=2020-01-02T00:00:00&user=1",
            headers=self.auth,
        )
        assert response.status_code == 404

        # fail when no events for user
        response = self.client.get(
            "/voice_event?since=2020-01-01T00:00:00&user=2",
            headers=self.auth,
        )
        assert response.status_code == 404
