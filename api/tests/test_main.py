from datetime import datetime
from unittest.mock import patch
from fastapi.testclient import TestClient
import pytest

from api.enums import ChannelType

from ..main import app
from .setup import client, session


DAY_BEFORE_EPOCH = datetime(2020, 1, 1)
DAY_IN_FIRST_EPOCH = datetime(2022, 3, 15)
DAY_IN_SECOND_EPOCH = datetime(2022, 4, 1)
DAY_IN_THIRD_EPOCH = datetime(2022, 4, 8)
DAY_IN_FOURTH_EPOCH = datetime(2022, 4, 15)

AUTH = {"Authorization": "Bearer hello"}
AUTH_WRONG = {"Authorization": "Bearer wrong"}


class TestMisc:
    def test_main(self, client):
        response = client.get(
            "/",
            headers=AUTH
        )
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}


def add_a_channel_and_member(client):
    response = client.put(
        "/member/1",
        headers=AUTH,
        json={
            "id": 1,
            "username": "test",
            "nickname": "nickname",
            "numbers": "1234",
        },
    )
    assert response.status_code == 200
    response = client.put(
        "/channel/1",
        headers=AUTH,
        json={
            "id": 1,
            "name": "test",
            "category": "test",
            "thread": False,
            "type": ChannelType.TEXT,
        },
    )
    assert response.status_code == 200


class TestMessages:
    def test_message(self, client):
        response = client.get(
            "/message/1",
            headers=AUTH,
        )
        assert response.status_code == 404

        add_a_channel_and_member(client)

        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello",
                "author": 1,
                "channel": 1,
            },
        )
        assert response.status_code == 200

        response = client.get(
            "/message/1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['id'] == '1'
        assert response.json()['timestamp'] == "2020-01-01T00:00:00"
        assert response.json()['content'] == 'hello'
        assert response.json()['author'] == '1'
        assert response.json()['channel'] == '1'
        assert response.json()['edited'] == False
        assert response.json()['edited_timestamp'] == None
        assert response.json()['deleted'] == False
        assert response.json()['pinned'] == False

    def test_message_with_attachments(self, client):
        response = client.get(
            "/message/1",
            headers=AUTH,
        )
        assert response.status_code == 404
        add_a_channel_and_member(client)

        response = client.put(
            "/message/1",
            headers=AUTH,
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
                    {
                        "msg_id": 1,
                        "url": "https://example.com/image3.png",
                        "sticker": True,
                    },
                ],
            },
        )
        assert response.status_code == 200

        response = client.get(
            "/message/1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['id'] == '1'
        assert response.json()['timestamp'] == "2020-01-01T00:00:00"
        assert response.json()['content'] == 'hello'
        assert response.json()['author'] == '1'
        assert response.json()['channel'] == '1'
        assert response.json()['edited'] == False
        assert response.json()['edited_timestamp'] == None
        assert response.json()['deleted'] == False
        assert response.json()['pinned'] == False
        assert response.json()['attachments'] == [
            {
                "msg_id": '1',
                "url": "https://example.com/image.png",
                "sticker": False,
            },
            {
                "msg_id": '1',
                "url": "https://example.com/image2.png",
                "sticker": False,
            },
            {
                "msg_id": '1',
                "url": "https://example.com/image3.png",
                "sticker": True,
            },
        ]

    def test_update_nonexistant_message(self, client):
        response = client.patch(
            "/message/1",
            headers=AUTH,
            json={
                "content": "new content",
                "edited": True,
                "edited_timestamp": "2020-01-01T00:00:00",
            },
        )
        assert response.status_code == 404

    def test_update_message(self, client):
        add_a_channel_and_member(client)
        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello",
                "author": 1,
                "channel": 1,
            },
        )
        assert response.status_code == 200

        response = client.patch(
            "/message/1",
            headers=AUTH,
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

        response = client.put(
            "/pin/1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['pinned'] == True

        response = client.patch(
            "/message/1",
            headers=AUTH,
            json={
                "deleted": True,
                "deleted_timestamp": "2020-01-01T00:00:00",
            },
        )
        assert response.status_code == 200
        assert response.json()['deleted'] == True
        assert response.json()['deleted_timestamp'] == '2020-01-01T00:00:00'

    def test_malformed_attachment_fails_to_create(self, client):
        response = client.put(
            "/message/1",
            headers=AUTH,
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

        response = client.put(
            "/message/1",
            headers=AUTH,
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
        response = client.put(
            "/pin/1",
            headers=AUTH,
        )
        assert response.status_code == 404

    def test_delete_nonexistant_message(self, client):
        response = client.delete(
            "/message/1",
            headers=AUTH,
        )
        assert response.status_code == 404

    def test_delete_message(self, client):
        add_a_channel_and_member(client)
        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello",
                "author": 1,
                "channel": 1,
            },
        )
        assert response.status_code == 200

        response = client.delete(
            "/message/1",
            headers=AUTH,
        )
        assert response.status_code == 200

        response = client.get(
            "/message/1",
            headers=AUTH,
        )
        assert response.status_code == 404


class TestMessagesExistanceResponses:
    def test_put_message_without_member_or_channel(self, client):
        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello",
                "author": 1,
                "channel": 1,
            },
        )
        assert response.status_code == 424
        assert response.json()['missing_members'] == ["1"]
        assert response.json()['missing_channels'] == ["1"]

    def test_put_message_without_member_or_channel_that_mentions(self, client):
        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello @fops",
                "author": 1,
                "channel": 1,
                "mentions": [{
                    "msg_id": "1",
                    "mention": "2",
                    "type": "member",
                }],
            },
        )
        assert response.status_code == 424
        assert set(response.json()['missing_members']) == {"1", "2"}
        assert response.json()['missing_channels'] == ["1"]

    def test_put_message_without_member_or_channel_that_replies(self, client):
        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello fops this is a reply",
                "author": 1,
                "channel": 1,
                "mentions": [{
                    "msg_id": "1",
                    "mention": "2",
                    "type": "member",
                }],
                "replying_to": "2"
            },
        )
        assert response.status_code == 424
        assert set(response.json()['missing_members']) == {"1", "2"}
        assert response.json()['missing_channels'] == ["1"]

    def test_put_message_without_member_or_channel_that_replies_without_mention(self, client):
        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello fops this is a reply",
                "author": 1,
                "channel": 1,
                "replying_to": "2"
            },
        )
        assert response.status_code == 424
        assert set(response.json()['missing_members']) == {"1", "2"}
        assert response.json()['missing_channels'] == ["1"]

    def test_put_message_with_member(self, client):
        add_a_channel_and_member(client)

        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello @fops",
                "author": 1,
                "channel": 1,
                "mentions": [{
                    "msg_id": "1",
                    "mention": "2",
                    "type": "member",
                }],
            },
        )
        assert response.status_code == 424
        assert response.json()['missing_members'] == ["2"]

        response = client.put(
            "/member/1",
            headers=AUTH,
            json={
                "id": 2,
                "username": "fops",
                "numbers": 8098,
            },
        )
        assert response.status_code == 200

        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello @fops",
                "author": 1,
                "channel": 1,
                "mentions": [{
                    "msg_id": "1",
                    "mention": "2",
                    "type": "member",
                }],
            },
        )
        assert response.status_code == 200

    def test_put_message_with_channel(self, client):
        add_a_channel_and_member(client)

        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": 1,
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello",
                "author": 1,
                "channel": 1,
            },
        )
        assert response.status_code == 200


class TestMultipleMessages:
    @ classmethod
    def setup_class(cls):
        patcher = patch('api.crud.datetime')
        mock_dt = patcher.start()
        mock_dt.now.return_value = DAY_IN_FOURTH_EPOCH
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        cls.patcher = patcher

    @ classmethod
    def teardown_class(cls):
        cls.patcher.stop()

    def test_getting_before_any_messages_fails(self, client):
        response = client.get(
            "/message?member_id=1",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.get(
            "/message?member_id=1&epoch=current",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.get(
            "/message?member_id=2&epoch=current",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.get(
            "/message?member_id=2&epoch=previous",
            headers=AUTH,
        )
        assert response.status_code == 404

    def test_get_multiple_messages_at_epoch(self, client):
        add_a_channel_and_member(client)
        
        response = client.put(
            "/member/2",
            headers=AUTH,
            json={
                "id": '2',
                "username": "member2",
                "nickname": "member2",
                "numbers": "4321",
            }
        )
        assert response.status_code == 200

        response = client.put(
            "/message/5",
            headers=AUTH,
            json={
                "id": '5',
                "timestamp": str(DAY_IN_FOURTH_EPOCH),
                "content": "hello",
                "author": '1',
                "channel": '1',
            },
        )
        assert response.status_code == 200

        response = client.put(
            "/message/2",
            headers=AUTH,
            json={
                "id": '2',
                "timestamp": str(DAY_IN_FOURTH_EPOCH),
                "content": "hello 2",
                "author": '1',
                "channel": '1',
            },
        )
        assert response.status_code == 200

        response = client.put(
            "/message/3",
            headers=AUTH,
            json={
                "id": '3',
                "timestamp": str(DAY_IN_FOURTH_EPOCH),
                "content": "hello 3",
                "author": '2',
                "channel": '1',
            },
        )
        assert response.status_code == 200

        response = client.get(
            "/message?member_id=1",
            headers=AUTH,
        )
        assert response.status_code == 200

        response = client.get(
            "/message?member_id=1&epoch=current",
            headers=AUTH,
        )
        assert response.status_code == 200

        response = client.get(
            "/message?member_id=2&epoch=current",
            headers=AUTH,
        )
        assert response.status_code == 200

        response = client.get(
            "/message?member_id=2&epoch=previous",
            headers=AUTH,
        )
        assert response.status_code == 404


class TestMessageMentions:
    def test_message_has_mentions(self, client):
        add_a_channel_and_member(client)

        response = client.put(
            "/member/2", headers=AUTH,
            json={"id": 2,"username": "fops","numbers": 8098,},
        )
        response = client.put(
            "/member/3", headers=AUTH,
            json={"id": 3,"username": "fops","numbers": 8098,},
        )

        response = client.put(
            "/message/1",
            headers=AUTH,
            json={
                "id": '1',
                "timestamp": "2020-01-01T00:00:00",
                "content": "hello @memberwithIDofTwo and @three and also @everyone and especially @league",
                "author": '1',
                "channel": '1',
                "mentions": [
                    {'msg_id': '1', 'mention': '2', 'type': 'member'},
                    {'msg_id': '1', 'mention': '3', 'type': 'member'},
                    {'msg_id': '1', 'mention': 'everyone', 'type': 'role'},
                    {'msg_id': '1', 'mention': '5', 'type': 'role'},
                ],
            },
        )
        assert response.status_code == 200

        response = client.get(
            "/message/1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['mentions'] == [
            {'msg_id': '1', 'mention': '2', 'type': 'member'},
            {'msg_id': '1', 'mention': '3', 'type': 'member'},
            {'msg_id': '1', 'mention': 'everyone', 'type': 'role'},
            {'msg_id': '1', 'mention': '5', 'type': 'role'},
        ]


class TestChannels:
    def test_channel(self, client):
        response = client.get(
            "/channel/1",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.put(
            "/channel/1",
            headers=AUTH,
            json={
                "id": 1,
                "name": "channel",
                "category": "general",
                "thread": False,
                "type": ChannelType.TEXT,
            }
        )
        assert response.status_code == 200

        response = client.get(
            "/channel/1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['id'] == '1'
        assert response.json()['name'] == 'channel'
        assert response.json()['category'] == 'general'
        assert response.json()['thread'] == False

    def test_update_nonexistant_channel(self, client):
        response = client.patch(
            "/channel/1",
            headers=AUTH,
            json={
                "name": "new name",
            },
        )
        assert response.status_code == 404

    def test_update_channel(self, client):
        response = client.put(
            "/channel/1",
            headers=AUTH,
            json={
                "id": 1,
                "name": "channel",
                "category": "general",
                "thread": False,
                "type": ChannelType.TEXT,
            }
        )
        assert response.status_code == 200
        assert response.json()['name'] != 'new channel'
        assert response.json()['category'] != 'general2'

        response = client.patch(
            "/channel/1",
            headers=AUTH,
            json={
                "name": "new channel",
                "category": "general2",
            }
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'new channel'
        assert response.json()['category'] == 'general2'

    def test_delete_nonexistant_channel(self, client):
        response = client.delete(
            "/channel/1",
            headers=AUTH,
        )
        assert response.status_code == 404

    def test_delete_channel(self, client):
        response = client.put(
            "/channel/1",
            headers=AUTH,
            json={
                "id": 1,
                "name": "channel",
                "category": "general",
                "thread": False,
                "type": ChannelType.TEXT,
            }
        )
        assert response.status_code == 200

        response = client.delete(
            "/channel/1",
            headers=AUTH,
        )
        assert response.status_code == 200

        response = client.get(
            "/channel/1",
            headers=AUTH,
        )
        assert response.status_code == 404


class TestMembers:
    def test_one_member(self, client):
        response = client.get(
            "/member/1",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.put(
            "/member/1",
            headers=AUTH,
            json={
                "id": 1,
                "username": "test",
                "nickname": "testname",
                "numbers": 8098,
            }
        )
        assert response.status_code == 200

        response = client.get(
            "/member/1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['id'] == '1'
        assert response.json()['username'] == 'test'
        assert response.json()['nickname'] == 'testname'
        assert response.json()['numbers'] == '8098'
        assert response.json()['bot'] == False

    def test_update_nonexistant_member(self, client):
        response = client.patch(
            "/member/1",
            headers=AUTH,
            json={
                "username": "new name",
            },
        )
        assert response.status_code == 404

    def test_update_member(self, client):
        response = client.put(
            "/member/1",
            headers=AUTH,
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
        assert response.json()['numbers'] == '8098'

        response = client.patch(
            "/member/1",
            headers=AUTH,
            json={
                "username": "new username",
                "nickname": "new nickname",
            }
        )
        assert response.status_code == 200
        assert response.json()['username'] == 'new username'
        assert response.json()['nickname'] == 'new nickname'
        assert response.json()['numbers'] == '8098'

    def test_multiple_members(self, client):
        response = client.get(
            "/member",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.put(
            "/member/1",
            headers=AUTH,
            json={
                "id": 1,
                "username": "test",
                "nickname": "testname",
                "numbers": 8098,
            }
        )
        response = client.put(
            "/member/2",
            headers=AUTH,
            json={
                "id": 2,
                "username": "test",
                "nickname": "testname",
                "numbers": 8098,
            }
        )
        response = client.get(
            "/member",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestBotMembers:
    def test_one_member(self, client):
        response = client.get(
            "/member/1",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.put(
            "/member/1",
            headers=AUTH,
            json={
                "id": 1,
                "username": "testbot",
                "nickname": "testname",
                "numbers": 8098,
                "bot": True,
            }
        )
        assert response.status_code == 200

        response = client.get(
            "/member/1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['id'] == '1'
        assert response.json()['username'] == 'testbot'
        assert response.json()['nickname'] == 'testname'
        assert response.json()['numbers'] == '8098'
        assert response.json()['bot'] == True


class TestEvents:
    @ classmethod
    def setup_class(cls):
        patcher = patch('api.crud.datetime')
        mock_dt = patcher.start()
        mock_dt.now.return_value = DAY_IN_THIRD_EPOCH
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        cls.patcher = patcher

    @ classmethod
    def teardown_class(cls):
        cls.patcher.stop()

    @pytest.mark.parametrize(
        "event_type", [
            "join",
            "leave",
            "move",
            "deafen",
            "undeafen",
            "mute",
            "unmute",
            "server deafen",
            "server undeafen",
            "server mute",
            "server unmute",
            "webcam start",
            "webcam stop",
            "stream start",
            "stream stop",
        ]
    )
    def test_voice_event(self, client, event_type):
        add_a_channel_and_member(client)

        response = client.get(
            "/voice_event?epoch=current",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.post(
            "/voice_event",
            headers=AUTH,
            json={
                "member_id": 1,
                "type": event_type,
                "channel": 1,
                "timestamp": str(DAY_IN_THIRD_EPOCH),
            }
        )
        assert response.status_code == 200

        response = client.get(
            "/voice_event?epoch=current",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['member_id'] == '1'
        assert response.json()[0]['type'] == event_type
        assert response.json()[0]['channel'] == '1'
        assert datetime.fromisoformat(response.json()[0]['timestamp']) \
            == DAY_IN_THIRD_EPOCH

        response = client.get(
            "/voice_event?member=1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['member_id'] == '1'

        # fail when epoch has no events
        response = client.get(
            "/voice_event?epoch=previous",
            headers=AUTH,
        )
        assert response.status_code == 404
        response = client.get(
            "/voice_event?epoch=1",
            headers=AUTH,
        )
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "event_type", [
            "not an event",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "",
        ]
    )
    def test_voice_event_invalid_type(self, client, event_type):
        response = client.post(
            "/voice_event",
            headers=AUTH,
            json={
                "member_id": 1,
                "type": event_type,
                "channel": 1,
                "timestamp": "2020-01-01T00:00:00",
            }
        )
        assert response.status_code == 422


class TestScores:
    @ classmethod
    def setup_class(cls):
        patcher = patch('api.crud.datetime')
        mock_dt = patcher.start()
        mock_dt.now.return_value = DAY_IN_THIRD_EPOCH
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        cls.patcher = patcher

    @ classmethod
    def teardown_class(cls):
        cls.patcher.stop()

    def test_get_scores_for_epoch(self, client):
        response = client.get(
            "/scores/current",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.post(
            "/scores",
            headers=AUTH,
            json=[
                {
                    "epoch": "1",
                    "member_id": 1,
                    "score": 2,
                },
                {
                    "epoch": "1",
                    "member_id": 2,
                    "score": 4,
                },
                {
                    "epoch": "1",
                    "member_id": 3,
                    "score": 8,
                }
            ]
        )
        assert response.status_code == 200
        assert response.json() == "success! 3 scores have been processed"

        response = client.get(
            "/scores/1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_epoch_semantics(self, client):
        response = client.get(
            "/score?epoch=current&member_id=1",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.post(
            "/scores",
            headers=AUTH,
            json=[
                {
                    "epoch": 1,
                    "member_id": 1,
                    "score": 2,
                },
                {
                    "epoch": 1,
                    "member_id": 2,
                    "score": 4,
                },
                {
                    "epoch": 1,
                    "member_id": 3,
                    "score": 8,
                },
                {
                    "epoch": 2,
                    "member_id": 1,
                    "score": 4,
                },
                {
                    "epoch": 3,
                    "member_id": 1,
                    "score": 8,
                }
            ]
        )
        assert response.status_code == 200

        response = client.get(
            "/score?epoch=current&member_id=1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['member_id'] == '1'
        assert response.json()['score'] == 8
        assert response.json() == client.get(
            "/score?epoch=3&member_id=1",
            headers=AUTH,
        ).json()

        response = client.get(
            "/score?epoch=previous&member_id=1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['member_id'] == '1'
        assert response.json()['score'] == 4
        assert response.json() == client.get(
            "/score?epoch=2&member_id=1",
            headers=AUTH,
        ).json()

        response = client.get(
            "/score?epoch=1&member_id=1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['member_id'] == '1'
        assert response.json()['score'] == 2

    def test_get_all_scores_for_epoch(self, client):
        response = client.post(
            "/scores",
            headers=AUTH,
            json=[
                {
                    "epoch": 1,
                    "member_id": 1,
                    "score": 2,
                },
                {
                    "epoch": 1,
                    "member_id": 2,
                    "score": 4,
                },
                {
                    "epoch": 1,
                    "member_id": 3,
                    "score": 8,
                },
                {
                    "epoch": 2,
                    "member_id": 1,
                    "score": 4,
                },
                {
                    "epoch": 3,
                    "member_id": 1,
                    "score": 8,
                }
            ]
        )
        assert response.status_code == 200

        response = client.get(
            "/scores/1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 3

        response = client.get(
            "/scores/2",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json() == client.get(
            "/scores/previous",
            headers=AUTH,
        ).json()

        response = client.get(
            "/scores/3",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json() == client.get(
            "/scores/current",
            headers=AUTH,
        ).json()

    def test_adding_user_creates_score(self, client):
        response = client.get(
            "/scores/3",
            headers=AUTH,
        )
        assert response.status_code == 404

        add_a_channel_and_member(client)
        
        response = client.get(
            "/scores/3",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()[0]['member_id'] == '1'

    @pytest.mark.parametrize(
        "get_route", [
            "/member/1/scores",
            "/member/name/test/scores",
            "/member/name/nickname/scores"
        ]
    )
    def test_get_scores_for_user(self, client, get_route):
        print(get_route)
        response = client.get(
            get_route,
            headers=AUTH,
        )
        assert response.status_code == 404

        add_a_channel_and_member(client)
        # add some scores
        response = client.post(
            "/scores",
            headers=AUTH,
            json=[
                {
                    "epoch": 1,
                    "member_id": 1,
                    "score": 2,
                },
                {
                    "epoch": 2,
                    "member_id": 1,
                    "score": 4,
                },
            ]
        )
        assert response.status_code == 200
        # get the scores
        response = client.get(
            get_route,
            headers=AUTH,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]['member_id'] == '1'
        assert data[1]['member_id'] == '1'
        assert data[2]['member_id'] == '1'
        scores = {x['score'] for x in data}
        assert scores == {2, 4, 750}
        dates = {x['date'] for x in data}
        assert dates == {'2022-04-01', '2022-04-08', '2022-01-01'}

    def test_getting_scores_for_epoch_includes_name(self, client):
        add_a_channel_and_member(client)

        # add two more members
        response = client.put(
            "/member/2",
            headers=AUTH,
            json={
                "id": 2,
                "username": "test2",
                "nickname": "nickname2",
                "numbers": "1111",
            }
        )
        assert response.status_code == 200
        response = client.put(
            "/member/3",
            headers=AUTH,
            json={
                "id": 3,
                "username": "test3",
                "nickname": "nickname3",
                "numbers": "1112",
            }
        )
        assert response.status_code == 200

        response = client.post(
            "/scores",
            headers=AUTH,
            json=[
                {
                    "epoch": 1,
                    "member_id": 1,
                    "score": 2,
                },
                {
                    "epoch": 1,
                    "member_id": 2,
                    "score": 4,
                },
                {
                    "epoch": 1,
                    "member_id": 3,
                    "score": 8,
                },
            ]
        )
        assert response.status_code == 200

        response = client.get(
            "/scores/named/1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 3
        print(response.json())
        dates = {x['date'] for x in response.json()}
        assert dates == {'2022-01-01'}
        names = {x['name'] for x in response.json()}
        assert names == {'nickname', 'nickname2', 'nickname3'}


class TestReactions:
    @ classmethod
    def setup_class(cls):
        patcher = patch('api.crud.datetime')
        mock_dt = patcher.start()
        mock_dt.now.return_value = DAY_IN_THIRD_EPOCH
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        cls.patcher = patcher

    @ classmethod
    def teardown_class(cls):
        cls.patcher.stop()

    def test_reaction(self, client):
        response = client.get(
            "/reaction?epoch=current&member_id=1",
            headers=AUTH,
        )
        assert response.status_code == 404

        response = client.post(
            "/reaction",
            headers=AUTH,
            json={
                "msg_id": 1,
                "member_id": 1,
                "emoji": "🐼",
                "timestamp": "2022-04-12T00:00:00",
            }
        )
        assert response.status_code == 200

        response = client.get(
            "/reaction?epoch=current&member_id=1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['member_id'] == '1'
        assert response.json()[0]['msg_id'] == '1'
        assert response.json()[0]['emoji'] == '🐼'
        assert response.json()[0]['timestamp'] == '2022-04-12T00:00:00'

        response = client.get(
            "/reaction?member_id=1",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]['member_id'] == '1'
        assert response.json()[0]['msg_id'] == '1'
        assert response.json()[0]['emoji'] == '🐼'
        assert response.json()[0]['timestamp'] == '2022-04-12T00:00:00'

        # fail when epoch has none
        response = client.get(
            "/reaction?epoch=previous&member_id=1",
            headers=AUTH,
        )
        assert response.status_code == 404

        # fail when no events for member
        response = client.get(
            "/reaction?epoch=current&member_id=2",
            headers=AUTH,
        )
        assert response.status_code == 404

    def test_delete_reactions(self, client):
        response = client.delete(
            "/reaction",
            headers=AUTH,
            json={
                "msg_id": 1,
                "member_id": 1,
                "emoji": "🐼",
            }
        )
        assert response.status_code == 404

        response = client.post(
            "/reaction",
            headers=AUTH,
            json={
                "msg_id": 1,
                "member_id": 1,
                "emoji": "🐼",
                "timestamp": "2022-04-12T00:00:00",
            }
        )
        assert response.status_code == 200

        response = client.delete(
            "/reaction",
            headers=AUTH,
            json={
                "msg_id": 1,
                "member_id": 1,
                "emoji": "🐼",
            }
        )
        assert response.status_code == 200
        assert response.json()['msg_id'] == '1'
        assert response.json()['member_id'] == '1'
        assert response.json()['emoji'] == '🐼'
        assert response.json()['timestamp'] == '2022-04-12T00:00:00'


class TestBeforeAnyEpoch:
    @ classmethod
    def setup_class(cls):
        patcher = patch('api.crud.datetime')
        mock_dt = patcher.start()
        mock_dt.now.return_value = DAY_BEFORE_EPOCH
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        cls.patcher = patcher

    @ classmethod
    def teardown_class(cls):
        cls.patcher.stop()

    def test_negative_epoch_not_found(self, client):
        response = client.get(
            "/epoch/-1",
            headers=AUTH,
        )
        assert response.status_code == 404

    def test_incorrect_semantic_epoch_not_found(self, client):
        response = client.get(
            "/epoch/hello",
            headers=AUTH,
        )
        assert response.status_code == 422

    def test_extremely_large_epoch_not_found(self, client):
        response = client.get(
            "/epoch/999999999",
            headers=AUTH,
        )
        assert response.status_code == 404

    def test_too_early_time_has_no_current(self, client):
        response = client.get(
            "/epoch/current",
            headers=AUTH,
        )
        assert response.status_code == 404

    def test_too_early_time_has_no_previous(self, client):
        response = client.get(
            "/epoch/previous",
            headers=AUTH,
        )
        assert response.status_code == 404


class TestDuringThirdEpoch:
    @ classmethod
    def setup_class(cls):
        patcher = patch('api.crud.datetime')
        mock_dt = patcher.start()
        mock_dt.now.return_value = DAY_IN_FOURTH_EPOCH
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        cls.patcher = patcher

    @ classmethod
    def teardown_class(cls):
        cls.patcher.stop()

    def test_current_epoch_is_fourth(self, client):
        response = client.get(
            "/epoch/current",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['id'] == 4

    def test_previous_epoch_is_third(self, client):
        response = client.get(
            "/epoch/previous",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert response.json()['id'] == 3

    def test_get_all_epochs(self, client):
        response = client.get(
            "/epoch/all",
            headers=AUTH,
        )
        assert response.status_code == 200
        assert len(response.json()) == 4


class TestAuth:
    def test_correct_auth(self, client):
        response = client.get(
            "/epoch/current",
            headers=AUTH,
        )
        assert response.status_code not in [403, 401]

    def test_missing_auth(self, client):
        response = client.get(
            "/epoch/current",
        )
        assert response.status_code == 403

    def test_wrong_auth(self, client):
        response = client.get(
            "/epoch/current",
            headers=AUTH_WRONG,
        )
        assert response.status_code == 401
