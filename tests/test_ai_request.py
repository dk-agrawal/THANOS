from app.ai.request import AIRequest, RequestType


def test_default_request_type():

    request = AIRequest(
        user_input="Hello THANOS"
    )

    assert request.request_type == (
        RequestType.CHAT
    )

    assert request.provider is None


def test_request_with_type():

    request = AIRequest(
        user_input="Search latest AI news",
        request_type=RequestType.RESEARCH,
    )

    assert request.user_input == (
        "Search latest AI news"
    )

    assert request.request_type == (
        RequestType.RESEARCH
    )


def test_request_with_provider():

    request = AIRequest(
        user_input="Hello",
        provider="openrouter",
    )

    assert request.provider == (
        "openrouter"
    )


def test_request_to_dict():

    request = AIRequest(
        user_input="Calculate 10 + 20",
        request_type=RequestType.CALCULATION,
        provider="openrouter",
    )

    assert request.to_dict() == {
        "user_input": "Calculate 10 + 20",
        "request_type": "calculation",
        "provider": "openrouter",
    }