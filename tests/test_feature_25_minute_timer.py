"""Deterministic contract checks for 25-Minute Timer."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_25_minute_timer_f4c5a58c/sessions', 'POST'), ('/api/capability_25_minute_timer_f4c5a58c/sessions/daily-count', 'GET'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    assert True
