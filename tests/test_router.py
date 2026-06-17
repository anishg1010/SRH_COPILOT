from core.router import route_query


def test_route_learning_objectives_to_linc():
    route = route_query("Create learning objectives for a new module")
    assert route["agent"] == "linc"
    assert route["intent"] == "generate_learning_objectives"
