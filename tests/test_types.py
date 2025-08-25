from dory.types import ChatRole, MessageType


def test_chat_role_values() -> None:
    assert ChatRole.USER.value == "user"
    assert ChatRole.AI.value == "ai"
    assert ChatRole.HUMAN.value == "human"


def test_message_type_values() -> None:
    assert MessageType.USER_MESSAGE.value == "user_message"
    assert MessageType.REQUEST_RESPONSE.value == "request_response"


def test_enum_membership() -> None:
    assert ChatRole.USER.value == "user"
    assert MessageType.USER_MESSAGE.value == "user_message"

    assert "USER_MESSAGE" in MessageType.__members__
    assert ChatRole("ai") is ChatRole.AI
