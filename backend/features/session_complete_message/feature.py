"""Session Complete Message Feature Module

This module provides a message display when a timer session reaches zero.
"""

from flask import Blueprint, jsonify, request
from http import HTTPStatus

blueprint = Blueprint('session_complete_message', __name__, url_prefix='/api/session-complete')


@blueprint.get('/message')
def get_session_complete_message():
    """Get the session complete message.
    
    Returns:
        JSON response with the session complete message
    """
    message = {
        'title': 'Session Complete!',
        'message': 'Your timer has reached zero. Great work!',
        'status': 'completed'
    }
    return jsonify(message), HTTPStatus.OK


@blueprint.post('/message')
def set_custom_session_complete_message():
    """Set a custom session complete message.
    
    Expected JSON body:
        {
            "title": "Custom Title",
            "message": "Custom message text"
        }
    
    Returns:
        JSON response confirming the custom message
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), HTTPStatus.BAD_REQUEST
    
    title = data.get('title', 'Session Complete!')
    message = data.get('message', 'Your timer has reached zero. Great work!')
    
    response = {
        'title': title,
        'message': message,
        'status': 'completed',
        'custom': True
    }
    
    return jsonify(response), HTTPStatus.OK


@blueprint.get('/message/default')
def get_default_session_complete_message():
    """Get the default session complete message.
    
    Returns:
        JSON response with the default session complete message
    """
    message = {
        'title': 'Session Complete!',
        'message': 'Your timer has reached zero. Great work!',
        'status': 'completed',
        'default': True
    }
    return jsonify(message), HTTPStatus.OK
