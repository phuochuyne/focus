"""Pause Timer feature module for Flask application.

This module provides functionality to pause a timer at its current time,
allowing students to handle interruptions during timed activities.
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
import time

blueprint = Blueprint('pause_timer', __name__, url_prefix='/api/pause-timer')


def require_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@blueprint.post('/pause')
@require_auth
def pause_timer():
    """Pause the timer at its current time.
    
    Expects JSON payload with:
    - timer_id: ID of the timer to pause
    - current_time: Current elapsed time in seconds
    
    Returns:
    - success: Boolean indicating operation success
    - paused_at: Timestamp when timer was paused
    - elapsed_time: Time elapsed when paused
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        timer_id = data.get('timer_id')
        current_time = data.get('current_time')
        
        if timer_id is None:
            return jsonify({'error': 'timer_id is required'}), 400
        
        if current_time is None:
            return jsonify({'error': 'current_time is required'}), 400
        
        # Validate current_time is a number
        try:
            elapsed_time = float(current_time)
        except (ValueError, TypeError):
            return jsonify({'error': 'current_time must be a number'}), 400
        
        if elapsed_time < 0:
            return jsonify({'error': 'current_time must be non-negative'}), 400
        
        # Store pause state in session
        session_key = f'timer_{timer_id}_paused'
        session_time_key = f'timer_{timer_id}_elapsed'
        
        paused_at = time.time()
        
        session[session_key] = True
        session[session_time_key] = elapsed_time
        session[f'timer_{timer_id}_paused_at'] = paused_at
        
        return jsonify({
            'success': True,
            'paused_at': paused_at,
            'elapsed_time': elapsed_time,
            'timer_id': timer_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to pause timer: {str(e)}'}), 500


@blueprint.post('/resume')
@require_auth
def resume_timer():
    """Resume a paused timer.
    
    Expects JSON payload with:
    - timer_id: ID of the timer to resume
    
    Returns:
    - success: Boolean indicating operation success
    - resumed_at: Timestamp when timer was resumed
    - elapsed_time: Time that was elapsed when paused
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        timer_id = data.get('timer_id')
        
        if timer_id is None:
            return jsonify({'error': 'timer_id is required'}), 400
        
        session_key = f'timer_{timer_id}_paused'
        session_time_key = f'timer_{timer_id}_elapsed'
        
        if not session.get(session_key):
            return jsonify({'error': 'Timer is not paused'}), 400
        
        elapsed_time = session.get(session_time_key, 0)
        resumed_at = time.time()
        
        # Clear pause state
        session.pop(session_key, None)
        session.pop(f'timer_{timer_id}_paused_at', None)
        session[f'timer_{timer_id}_resumed_at'] = resumed_at
        
        return jsonify({
            'success': True,
            'resumed_at': resumed_at,
            'elapsed_time': elapsed_time,
            'timer_id': timer_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to resume timer: {str(e)}'}), 500


@blueprint.get('/status/<timer_id>')
@require_auth
def get_timer_status(timer_id):
    """Get the current pause status of a timer.
    
    Args:
        timer_id: ID of the timer to check
    
    Returns:
    - is_paused: Boolean indicating if timer is paused
    - elapsed_time: Time elapsed when paused (if paused)
    - paused_at: Timestamp when paused (if paused)
    """
    try:
        session_key = f'timer_{timer_id}_paused'
        session_time_key = f'timer_{timer_id}_elapsed'
        session_paused_at_key = f'timer_{timer_id}_paused_at'
        
        is_paused = session.get(session_key, False)
        
        response = {
            'timer_id': timer_id,
            'is_paused': is_paused
        }
        
        if is_paused:
            response['elapsed_time'] = session.get(session_time_key, 0)
            response['paused_at'] = session.get(session_paused_at_key)
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get timer status: {str(e)}'}), 500


@blueprint.delete('/clear/<timer_id>')
@require_auth
def clear_timer_state(timer_id):
    """Clear all pause state for a timer.
    
    Args:
        timer_id: ID of the timer to clear
    
    Returns:
    - success: Boolean indicating operation success
    """
    try:
        session.pop(f'timer_{timer_id}_paused', None)
        session.pop(f'timer_{timer_id}_elapsed', None)
        session.pop(f'timer_{timer_id}_paused_at', None)
        session.pop(f'timer_{timer_id}_resumed_at', None)
        
        return jsonify({
            'success': True,
            'timer_id': timer_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to clear timer state: {str(e)}'}), 500
