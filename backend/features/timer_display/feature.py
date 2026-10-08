from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import time

blueprint = Blueprint('timer_display', __name__, url_prefix='/api/timer-display')

# In-memory storage for timer state (in production, consider Redis or database)
timer_state = {
    'start_time': None,
    'duration_seconds': 0,
    'is_running': False,
    'paused_time': 0
}


@blueprint.get('/current')
def get_current_timer():
    """
    Get the current timer display showing countdown time in minutes and seconds.
    Returns the remaining time in the format MM:SS.
    """
    try:
        if not timer_state['is_running']:
            # Timer is not running, return the paused time or zero
            remaining_seconds = max(0, timer_state['paused_time'])
        else:
            # Timer is running, calculate remaining time
            elapsed = time.time() - timer_state['start_time']
            remaining_seconds = max(0, timer_state['duration_seconds'] - elapsed)
            
            # Auto-stop timer if it reaches zero
            if remaining_seconds == 0:
                timer_state['is_running'] = False
                timer_state['paused_time'] = 0
        
        # Convert to minutes and seconds
        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)
        
        return jsonify({
            'success': True,
            'display': f'{minutes:02d}:{seconds:02d}',
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': int(remaining_seconds),
            'is_running': timer_state['is_running']
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@blueprint.post('/start')
def start_timer():
    """
    Start or restart the timer with a specified duration.
    Expects JSON body with 'duration_seconds' or 'minutes'.
    """
    try:
        data = request.get_json() or {}
        
        # Accept either duration_seconds or minutes
        if 'duration_seconds' in data:
            duration = int(data['duration_seconds'])
        elif 'minutes' in data:
            duration = int(data['minutes']) * 60
        else:
            return jsonify({
                'success': False,
                'error': 'Missing duration_seconds or minutes parameter'
            }), 400
        
        if duration <= 0:
            return jsonify({
                'success': False,
                'error': 'Duration must be positive'
            }), 400
        
        # Start the timer
        timer_state['start_time'] = time.time()
        timer_state['duration_seconds'] = duration
        timer_state['is_running'] = True
        timer_state['paused_time'] = duration
        
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        return jsonify({
            'success': True,
            'message': 'Timer started',
            'display': f'{minutes:02d}:{seconds:02d}',
            'duration_seconds': duration
        }), 200
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid duration value'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@blueprint.post('/pause')
def pause_timer():
    """
    Pause the currently running timer.
    """
    try:
        if not timer_state['is_running']:
            return jsonify({
                'success': False,
                'error': 'Timer is not running'
            }), 400
        
        # Calculate remaining time and pause
        elapsed = time.time() - timer_state['start_time']
        remaining = max(0, timer_state['duration_seconds'] - elapsed)
        
        timer_state['is_running'] = False
        timer_state['paused_time'] = remaining
        
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        return jsonify({
            'success': True,
            'message': 'Timer paused',
            'display': f'{minutes:02d}:{seconds:02d}',
            'remaining_seconds': int(remaining)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@blueprint.post('/resume')
def resume_timer():
    """
    Resume a paused timer.
    """
    try:
        if timer_state['is_running']:
            return jsonify({
                'success': False,
                'error': 'Timer is already running'
            }), 400
        
        if timer_state['paused_time'] <= 0:
            return jsonify({
                'success': False,
                'error': 'No paused timer to resume'
            }), 400
        
        # Resume with remaining time
        timer_state['start_time'] = time.time()
        timer_state['duration_seconds'] = timer_state['paused_time']
        timer_state['is_running'] = True
        
        minutes = int(timer_state['paused_time'] // 60)
        seconds = int(timer_state['paused_time'] % 60)
        
        return jsonify({
            'success': True,
            'message': 'Timer resumed',
            'display': f'{minutes:02d}:{seconds:02d}'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@blueprint.post('/stop')
def stop_timer():
    """
    Stop and reset the timer.
    """
    try:
        timer_state['start_time'] = None
        timer_state['duration_seconds'] = 0
        timer_state['is_running'] = False
        timer_state['paused_time'] = 0
        
        return jsonify({
            'success': True,
            'message': 'Timer stopped',
            'display': '00:00'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@blueprint.get('/status')
def get_timer_status():
    """
    Get detailed timer status information.
    """
    try:
        if timer_state['is_running']:
            elapsed = time.time() - timer_state['start_time']
            remaining_seconds = max(0, timer_state['duration_seconds'] - elapsed)
        else:
            remaining_seconds = timer_state['paused_time']
        
        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)
        
        return jsonify({
            'success': True,
            'is_running': timer_state['is_running'],
            'display': f'{minutes:02d}:{seconds:02d}',
            'remaining_seconds': int(remaining_seconds),
            'minutes': minutes,
            'seconds': seconds
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
