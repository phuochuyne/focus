"""
No Tutorial on Launch Feature Module

This module ensures the timer interface is shown directly on launch
without any tutorial or permission prompts.
"""

from flask import Blueprint, jsonify

blueprint = Blueprint('no_tutorial_on_launch', __name__)


@blueprint.get('/api/launch-config')
def get_launch_config():
    """
    Returns the launch configuration indicating no tutorial should be shown.
    
    Returns:
        JSON response with launch configuration
    """
    return jsonify({
        'show_tutorial': False,
        'show_permissions_prompt': False,
        'direct_to_timer': True,
        'feature': 'no_tutorial_on_launch'
    }), 200


@blueprint.get('/api/tutorial-status')
def get_tutorial_status():
    """
    Returns the tutorial status for the application.
    
    Returns:
        JSON response indicating tutorial is disabled
    """
    return jsonify({
        'tutorial_enabled': False,
        'tutorial_completed': True,
        'skip_tutorial': True
    }), 200


@blueprint.get('/api/onboarding-config')
def get_onboarding_config():
    """
    Returns onboarding configuration that skips all onboarding flows.
    
    Returns:
        JSON response with onboarding configuration
    """
    return jsonify({
        'onboarding_required': False,
        'show_welcome_screen': False,
        'show_feature_tour': False,
        'immediate_access': True
    }), 200
