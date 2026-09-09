import pytest

from app.ai.classifier import AIRequestClassifier
from app.ai.request import RequestType


@pytest.fixture
def classifier():

    return AIRequestClassifier()


def test_classifies_chat(classifier):

    request = classifier.classify(
        "Hello THANOS"
    )

    assert request.request_type == (
        RequestType.CHAT
    )


def test_classifies_calculation(classifier):

    request = classifier.classify(
        "Calculate 25 * 8"
    )

    assert request.request_type == (
        RequestType.CALCULATION
    )


def test_classifies_research(classifier):

    request = classifier.classify(
        "Research latest AI trends"
    )

    assert request.request_type == (
        RequestType.RESEARCH
    )


def test_classifies_tool_request(classifier):

    request = classifier.classify(
        "What's the weather in Bhopal?"
    )

    assert request.request_type == (
        RequestType.TOOL
    )


def test_strips_input(classifier):

    request = classifier.classify(
        "   Hello THANOS   "
    )

    assert request.user_input == (
        "Hello THANOS"
    )


def test_empty_input_is_rejected(classifier):

    with pytest.raises(
        ValueError,
        match="User input cannot be empty",
    ):

        classifier.classify("   ")


def test_github_request_is_tool(classifier):

    request = classifier.classify(
        "Show me this GitHub repository"
    )

    assert request.request_type == (
        RequestType.TOOL
    )


def test_research_has_priority_over_generic_tool(
    classifier,
):

    request = classifier.classify(
        "Research latest weather trends"
    )

    assert request.request_type == (
        RequestType.RESEARCH
    )