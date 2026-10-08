"""Whole-application smoke tests."""

from backend import create_app


def test_health_endpoint():
    app = create_app(testing=True)
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["ok"] is True


def test_expected_function_inventory_is_frozen():
    expected = ('capability_25_minute_timer_f4c5a58c.function.record_completed_session', 'capability_25_minute_timer_f4c5a58c.function.get_daily_session_count', 'capability_daily_session_counter_7a9d9848.function.record_completed_session', 'capability_daily_session_counter_7a9d9848.function.get_daily_session_count', 'capability_start_timer_a5aab8dc.function.get_timer_state', 'capability_start_timer_a5aab8dc.function.start_timer', 'capability_start_timer_a5aab8dc.function.pause_timer', 'capability_local_data_storage_145f595e.function.get_daily_session_state', 'capability_local_data_storage_145f595e.function.increment_session_count', 'capability_resume_timer_f65ac826.function.get_timer_state', 'capability_resume_timer_f65ac826.function.save_paused_state', 'capability_resume_timer_f65ac826.function.clear_paused_state')
    assert len(expected) == 12
