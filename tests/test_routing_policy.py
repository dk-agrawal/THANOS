import pytest

from app.ai.request import RequestType
from app.ai.routing_policy import (
    AIRoutingPolicy,
)


@pytest.fixture
def policy():

    return AIRoutingPolicy(
        default_provider="openrouter"
    )


def test_chat_routing(policy):

    decision = policy.decide(
        RequestType.CHAT
    )

    assert decision.provider == (
        "openrouter"
    )

    assert decision.use_tools is False
    assert decision.use_research is False


def test_calculation_routing(policy):

    decision = policy.decide(
        RequestType.CALCULATION
    )

    assert decision.use_tools is True
    assert decision.use_research is False


def test_tool_routing(policy):

    decision = policy.decide(
        RequestType.TOOL
    )

    assert decision.use_tools is True
    assert decision.use_research is False


def test_research_routing(policy):

    decision = policy.decide(
        RequestType.RESEARCH
    )

    assert decision.use_tools is True
    assert decision.use_research is True


def test_custom_provider(policy):

    decision = policy.decide(
        RequestType.CHAT,
        provider="custom-provider",
    )

    assert decision.provider == (
        "custom-provider"
    )


def test_empty_default_provider_rejected():

    with pytest.raises(
        ValueError,
        match="Default provider cannot be empty",
    ):

        AIRoutingPolicy(
            default_provider=""
        )


def test_decision_to_dict(policy):

    decision = policy.decide(
        RequestType.RESEARCH
    )

    assert decision.to_dict() == {
        "request_type": "research",
        "provider": "openrouter",
        "use_tools": True,
        "use_research": True,
    }