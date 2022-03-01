from datetime import datetime
from unittest.mock import patch
from fastapi.testclient import TestClient

from ..main import app
from .setup import client, session


class TestMisc:
    app = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    def test_main(self):
        response = self.app.get(
            "/",
            headers=self.auth
        )
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}


class TestMessages:
    app = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    def test_message(self, client):
        response = self.app.get(
            "/message/1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.app.put(
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

        response = self.app.get(
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
        response = self.app.get(
            "/message/1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.app.put(
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

        response = self.app.get(
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
        response = self.app.patch(
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
        response = self.app.put(
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

        response = self.app.patch(
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

        response = self.app.put(
            "/pin/1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['pinned'] == True

        response = self.app.patch(
            "/message/1",
            headers=self.auth,
            json={
                "deleted": True,
            },
        )
        assert response.status_code == 200
        assert response.json()['deleted'] == True

    def test_malformed_attachment_fails_to_create(self, client):
        response = self.app.put(
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
                    }
                ],
            },
        )
        assert response.status_code == 422

        response = self.app.put(
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
                        "the_number_one": 1,
                    }
                ],
            },
        )
        assert response.status_code == 422

    def test_pin_nonexistant_message(self, client):
        response = self.app.put(
            "/pin/1",
            headers=self.auth,
        )
        assert response.status_code == 404

    def test_delete_nonexistant_message(self, client):
        response = self.app.delete(
            "/message/1",
            headers=self.auth,
        )
        assert response.status_code == 404

    def test_delete_message(self, client):
        response = self.app.put(
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

        response = self.app.delete(
            "/message/1",
            headers=self.auth,
        )
        assert response.status_code == 200

        response = self.app.get(
            "/message/1",
            headers=self.auth,
        )
        assert response.status_code == 404


class TestChannels:
    app = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    def test_channel(self, client):
        response = self.app.get(
            "/channel/1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.app.put(
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

        response = self.app.get(
            "/channel/1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['id'] == 1
        assert response.json()['name'] == 'channel'
        assert response.json()['category'] == 'general'
        assert response.json()['thread'] == False

    def test_update_nonexistant_channel(self, client):
        response = self.app.patch(
            "/channel/1",
            headers=self.auth,
            json={
                "name": "new name",
            },
        )
        assert response.status_code == 404

    def test_update_channel(self, client):
        response = self.app.put(
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

        response = self.app.patch(
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
    app = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    def test_user(self, client):
        response = self.app.get(
            "/user/1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.app.put(
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

        response = self.app.get(
            "/user/1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['id'] == 1
        assert response.json()['username'] == 'test'
        assert response.json()['nickname'] == 'testname'
        assert response.json()['numbers'] == 8098

    def test_update_nonexistant_user(self, client):
        response = self.app.patch(
            "/user/1",
            headers=self.auth,
            json={
                "username": "new name",
            },
        )
        assert response.status_code == 404

    def test_update_user(self, client):
        response = self.app.put(
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

        response = self.app.patch(
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
    app = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    def test_voice_event(self, client):
        response = self.app.get(
            "/voice_event?since=2020-01-01T00:00:00&user=1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.app.post(
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

        response = self.app.get(
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
        response = self.app.get(
            "/voice_event?since=2020-01-02T00:00:00&user=1",
            headers=self.auth,
        )
        assert response.status_code == 404

        # fail when no events for user
        response = self.app.get(
            "/voice_event?since=2020-01-01T00:00:00&user=2",
            headers=self.auth,
        )
        assert response.status_code == 404


class TestScores:
    app = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    @classmethod
    def setup_class(cls):
        patcher = patch('api.crud.datetime')
        mock_dt = patcher.start()
        mock_dt.now.return_value = datetime(2022, 4, 13)
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        cls.patcher = patcher

    @classmethod
    def teardown_class(cls):
        cls.patcher.stop()

    def test_get_scores_for_epoch(self, client):
        response = self.app.get(
            "/scores?epoch=current",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.app.post(
            "/scores",
            headers=self.auth,
            json=[
                {
                    "epoch": "1",
                    "user_id": 1,
                    "score": 2,
                },
                {
                    "epoch": "1",
                    "user_id": 2,
                    "score": 4,
                },
                {
                    "epoch": "1",
                    "user_id": 3,
                    "score": 8,
                }
            ]
        )
        assert response.status_code == 200
        assert response.json() == "success! 3 scores have been processed"

        response = self.app.get(
            "/scores?epoch=1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_get_scores_for_user_at_epoch(self, client):
        response = self.app.get(
            "/score?epoch=1&user_id=1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.app.post(
            "/scores",
            headers=self.auth,
            json=[
                {
                    "epoch": 1,
                    "user_id": 1,
                    "score": 2,
                },
                {
                    "epoch": 1,
                    "user_id": 2,
                    "score": 4,
                },
                {
                    "epoch": 1,
                    "user_id": 3,
                    "score": 8,
                },
                {
                    "epoch": 2,
                    "user_id": 1,
                    "score": 4,
                },
                {
                    "epoch": 3,
                    "user_id": 1,
                    "score": 8,
                },
            ]
        )
        assert response.status_code == 200

        response = self.app.get(
            "/score?epoch=1&user_id=1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['user_id'] == 1
        assert response.json()['score'] == 2

    def test_epoch_semantics(self, client):

        response = self.app.get(
            "/score?epoch=current&user_id=1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.app.post(
            "/scores",
            headers=self.auth,
            json=[
                {
                    "epoch": 1,
                    "user_id": 1,
                    "score": 2,
                },
                {
                    "epoch": 1,
                    "user_id": 2,
                    "score": 4,
                },
                {
                    "epoch": 1,
                    "user_id": 3,
                    "score": 8,
                },
                {
                    "epoch": 2,
                    "user_id": 1,
                    "score": 4,
                },
                {
                    "epoch": 3,
                    "user_id": 1,
                    "score": 8,
                }
            ]
        )
        assert response.status_code == 200

        response = self.app.get(
            "/score?epoch=current&user_id=1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['user_id'] == 1
        assert response.json()['score'] == 8
        assert response.json() == self.app.get(
            "/score?epoch=3&user_id=1",
            headers=self.auth,
        ).json()

        response = self.app.get(
            "/score?epoch=previous&user_id=1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['user_id'] == 1
        assert response.json()['score'] == 4
        assert response.json() == self.app.get(
            "/score?epoch=2&user_id=1",
            headers=self.auth,
        ).json()

        response = self.app.get(
            "/score?epoch=1&user_id=1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert response.json()['user_id'] == 1
        assert response.json()['score'] == 2

    def test_get_all_scores_for_epoch(self, client):

        response = self.app.post(
            "/scores",
            headers=self.auth,
            json=[
                {
                    "epoch": 1,
                    "user_id": 1,
                    "score": 2,
                },
                {
                    "epoch": 1,
                    "user_id": 2,
                    "score": 4,
                },
                {
                    "epoch": 1,
                    "user_id": 3,
                    "score": 8,
                },
                {
                    "epoch": 2,
                    "user_id": 1,
                    "score": 4,
                },
                {
                    "epoch": 3,
                    "user_id": 1,
                    "score": 8,
                }
            ]
        )
        assert response.status_code == 200

        response = self.app.get(
            "/scores?epoch=1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert len(response.json()) == 3

        response = self.app.get(
            "/scores?epoch=2",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json() == self.app.get(
            "/scores?epoch=previous",
            headers=self.auth,
        ).json()

        response = self.app.get(
            "/scores?epoch=3",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json() == self.app.get(
            "/scores?epoch=current",
            headers=self.auth,
        ).json()


class TestReactions():
    app = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    @classmethod
    def setup_class(cls):
        patcher = patch('api.crud.datetime')
        mock_dt = patcher.start()
        mock_dt.now.return_value = datetime(2022, 4, 13)
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        cls.patcher = patcher

    @classmethod
    def teardown_class(cls):
        cls.patcher.stop()

    def test_reaction(self, client):
        response = self.app.get(
            "/reaction?epoch=current&user_id=1",
            headers=self.auth,
        )
        assert response.status_code == 404

        response = self.app.post(
            "/reaction",
            headers=self.auth,
            json={
                "msg_id": 1,
                "user_id": 1,
                "emoji": "🐼",
                "timestamp": "2022-04-12T00:00:00",
            }
        )
        assert response.status_code == 200

        response = self.app.get(
            "/reaction?epoch=current&user_id=1",
            headers=self.auth,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['user_id'] == 1
        assert response.json()[0]['msg_id'] == 1
        assert response.json()[0]['emoji'] == '🐼'
        assert response.json()[0]['timestamp'] == '2022-04-12T00:00:00'

        # fail when epoch has none
        response = self.app.get(
            "/reaction?epoch=previous&user_id=1",
            headers=self.auth,
        )
        assert response.status_code == 404

        # fail when no events for user
        response = self.app.get(
            "/reaction?epoch=current&user_id=2",
            headers=self.auth,
        )
        assert response.status_code == 404

    def test_delete_reactions(self, client):
        response = self.app.delete(
            "/reaction",
            headers=self.auth,
            json={
                "msg_id": 1,
                "user_id": 1,
                "emoji": "🐼",
            }
        )
        assert response.status_code == 404

        response = self.app.post(
            "/reaction",
            headers=self.auth,
            json={
                "msg_id": 1,
                "user_id": 1,
                "emoji": "🐼",
                "timestamp": "2022-04-12T00:00:00",
            }
        )
        assert response.status_code == 200

        response = self.app.delete(
            "/reaction",
            headers=self.auth,
            json={
                "msg_id": 1,
                "user_id": 1,
                "emoji": "🐼",
            }
        )
        assert response.status_code == 200
        assert response.json()['msg_id'] == 1
        assert response.json()['user_id'] == 1
        assert response.json()['emoji'] == '🐼'
        assert response.json()['timestamp'] == '2022-04-12T00:00:00'


class TestEpoch:
    app = TestClient(app)
    auth = {"Authorization": "Bearer hello"}

    @classmethod
    def setup_class(cls):
        patcher = patch('api.crud.datetime')
        mock_dt = patcher.start()
        mock_dt.now.return_value = datetime(2020, 4, 13)
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        cls.patcher = patcher

    @classmethod
    def teardown_class(cls):
        cls.patcher.stop()
    
    def test_negative_epoch_not_found(self, client):
        response = self.app.get(
            "/scores?epoch=-1",
            headers=self.auth,
        )
        assert response.status_code == 404

    def test_incorrect_semantic_epoch_not_found(self, client):
        response = self.app.get(
            "/scores?epoch=hello",
            headers=self.auth,
        )
        assert response.status_code == 422

    def test_extremely_large_epoch_not_found(self, client):
        response = self.app.get(
            "/scores?epoch=999999999",
            headers=self.auth,
        )
        assert response.status_code == 404

    def test_too_early_time_has_no_current(self, client):
        response = self.app.get(
            "/scores?epoch=current",
            headers=self.auth,
        )
        assert response.status_code == 404

    def test_too_early_time_has_no_previous(self, client):
        response = self.app.get(
            "/scores?epoch=previous",
            headers=self.auth,
        )
        assert response.status_code == 404