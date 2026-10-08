"""Session Completion Sound feature module.

This module provides a simple alert sound that plays when a timer reaches zero.
Since no database tables or specific functions are required, this module provides
a basic endpoint to serve the completion sound file.
"""

from flask import Blueprint, jsonify, send_file, current_app
import os

blueprint = Blueprint('session_completion_sound', __name__)


@blueprint.get('/api/session-completion-sound')
def get_completion_sound():
    """Serve the session completion sound file.
    
    Returns:
        Audio file response or error if file not found
    """
    try:
        # Look for sound file in the static/sounds directory
        sound_path = os.path.join(
            current_app.root_path, 
            'static', 
            'sounds', 
            'completion.mp3'
        )
        
        if os.path.exists(sound_path):
            return send_file(
                sound_path,
                mimetype='audio/mpeg',
                as_attachment=False
            )
        else:
            # Return a success response indicating sound should be played client-side
            return jsonify({
                'success': True,
                'message': 'Play completion sound',
                'sound_type': 'default'
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve completion sound',
            'details': str(e)
        }), 500


@blueprint.post('/api/session-completion-sound/trigger')
def trigger_completion_sound():
    """Trigger endpoint for session completion sound.
    
    This endpoint can be called when a session completes to log or track
    completion sound events.
    
    Returns:
        JSON response indicating sound should be played
    """
    return jsonify({
        'success': True,
        'message': 'Session completed',
        'play_sound': True,
        'sound_type': 'completion'
    }), 200


@blueprint.get('/api/session-completion-sound/config')
def get_sound_config():
    """Get configuration for the session completion sound.
    
    Returns:
        JSON configuration for the completion sound
    """
    return jsonify({
        'success': True,
        'config': {
            'enabled': True,
            'sound_type': 'alert',
            'duration_ms': 1000,
            'volume': 0.8,
            'description': 'A short, simple alert sound that plays when the timer reaches zero'
        }
    }), 200
