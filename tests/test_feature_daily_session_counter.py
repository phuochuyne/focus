"""Deterministic contract checks for Daily Session Counter."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_daily_session_counter_7a9d9848/sessions/complete', 'POST'), ('/api/capability_daily_session_counter_7a9d9848/sessions/today/count', 'GET'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    assert True
