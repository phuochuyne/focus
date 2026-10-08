from flask import Blueprint, jsonify

blueprint = Blueprint('reset_timer', __name__)

@blueprint.post('/api/timer/reset')
def reset_timer():
    """
    Reset the timer to 25:00 (25 minutes).
    
    Returns:
        JSON response with the reset timer value in seconds
    """
    default_timer_seconds = 25 * 60  # 25 minutes in seconds
    
    return jsonify({
        'success': True,
        'timer_seconds': default_timer_seconds,
        'timer_display': '25:00',
        'message': 'Timer reset to 25:00'
    }), 200
