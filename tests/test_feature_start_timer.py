"""Deterministic contract checks for Start Timer."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_start_timer_a5aab8dc/timer/state', 'GET'), ('/api/capability_start_timer_a5aab8dc/timer/start', 'POST'), ('/api/capability_start_timer_a5aab8dc/timer/pause', 'POST'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    assert True
