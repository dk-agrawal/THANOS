from app.agents.quality import ResearchQualityGate


def test_research_quality_gate():

    gate = ResearchQualityGate()

    assert gate is not None


def test_research_quality_gate_empty_results():

    gate = ResearchQualityGate()

    result = gate.validate(
        research_data={}
    )

    assert result["passed"] is False

    assert result["reason"] == (
        "No research sources available."
    )


def test_research_quality_gate_low_quality_sources():

    gate = ResearchQualityGate()

    research_data = {
        "sources": {
            "news": {
                "score": {
                    "value": 0
                },
                "items": [],
            }
        }
    }

    result = gate.validate(
        research_data
    )

    assert result["passed"] is False


def test_research_quality_gate_good_research():

        gate = ResearchQualityGate()

        research_data = {
            "sources": {
                "news": {
                    "score": {
                        "value": 50
                    },
                    "items": [
                        {
                            "score": {
                                "value": 50
                            }
                        }
                    ],
                }
            }
        }

        result = gate.validate(
            research_data
        )

        assert result["passed"] is True

        assert result["successful_sources"] == 1
        assert result["useful_items"] == 1
        assert result["best_result_score"] == 50