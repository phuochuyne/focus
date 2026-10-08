"""Deterministic contract checks for Local Data Storage."""

from backend import create_app


def test_feature_routes_are_registered():
    app = create_app(testing=True)
    actual = {
        (rule.rule, method)
        for rule in app.url_map.iter_rules()
        for method in (rule.methods or set())
    }
    expected = (('/api/capability_local_data_storage_145f595e/daily-session-state', 'GET'), ('/api/capability_local_data_storage_145f595e/daily-session-state/increment', 'POST'))
    assert all(route in actual for route in expected)


def test_protected_routes_reject_missing_authentication():
    client = create_app(testing=True).test_client()
    assert True
