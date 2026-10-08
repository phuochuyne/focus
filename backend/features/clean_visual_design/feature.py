"""Clean Visual Design feature module.

This module provides a Flask blueprint for serving clean visual design assets
and configuration. It ensures a consistent, high-contrast visual style across
the application with no theme customization options.
"""

from flask import Blueprint, jsonify, current_app
from functools import wraps
import logging

logger = logging.getLogger(__name__)

blueprint = Blueprint('clean_visual_design', __name__, url_prefix='/api/visual-design')


def handle_errors(f):
    """Decorator to handle errors consistently across endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function


@blueprint.get('/config')
@handle_errors
def get_visual_config():
    """Get the visual design configuration.
    
    Returns the default clean visual design settings including colors,
    typography, spacing, and contrast settings.
    """
    config = {
        'theme': 'clean',
        'colors': {
            'primary': '#000000',
            'secondary': '#333333',
            'background': '#FFFFFF',
            'text': '#000000',
            'textSecondary': '#666666',
            'border': '#CCCCCC',
            'error': '#D32F2F',
            'success': '#388E3C',
            'warning': '#F57C00',
            'info': '#1976D2'
        },
        'typography': {
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            'fontSize': {
                'base': '16px',
                'small': '14px',
                'large': '18px',
                'h1': '32px',
                'h2': '28px',
                'h3': '24px',
                'h4': '20px',
                'h5': '18px',
                'h6': '16px'
            },
            'fontWeight': {
                'normal': 400,
                'medium': 500,
                'bold': 700
            },
            'lineHeight': {
                'tight': 1.2,
                'normal': 1.5,
                'relaxed': 1.75
            }
        },
        'spacing': {
            'xs': '4px',
            'sm': '8px',
            'md': '16px',
            'lg': '24px',
            'xl': '32px',
            'xxl': '48px'
        },
        'borderRadius': {
            'none': '0px',
            'sm': '2px',
            'md': '4px',
            'lg': '8px',
            'full': '9999px'
        },
        'shadows': {
            'none': 'none',
            'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
        },
        'contrast': {
            'level': 'high',
            'ratio': 7.0,
            'description': 'WCAG AAA compliant contrast ratios'
        },
        'customization': {
            'enabled': False,
            'themeSwitcher': False,
            'colorPicker': False,
            'description': 'No personalization options available'
        }
    }
    
    return jsonify(config), 200


@blueprint.get('/styles')
@handle_errors
def get_css_variables():
    """Get CSS custom properties for the clean visual design.
    
    Returns CSS variables that can be injected into the application
    for consistent styling.
    """
    css_vars = {
        '--color-primary': '#000000',
        '--color-secondary': '#333333',
        '--color-background': '#FFFFFF',
        '--color-text': '#000000',
        '--color-text-secondary': '#666666',
        '--color-border': '#CCCCCC',
        '--color-error': '#D32F2F',
        '--color-success': '#388E3C',
        '--color-warning': '#F57C00',
        '--color-info': '#1976D2',
        '--font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        '--font-size-base': '16px',
        '--font-size-small': '14px',
        '--font-size-large': '18px',
        '--font-size-h1': '32px',
        '--font-size-h2': '28px',
        '--font-size-h3': '24px',
        '--font-size-h4': '20px',
        '--font-size-h5': '18px',
        '--font-size-h6': '16px',
        '--font-weight-normal': '400',
        '--font-weight-medium': '500',
        '--font-weight-bold': '700',
        '--line-height-tight': '1.2',
        '--line-height-normal': '1.5',
        '--line-height-relaxed': '1.75',
        '--spacing-xs': '4px',
        '--spacing-sm': '8px',
        '--spacing-md': '16px',
        '--spacing-lg': '24px',
        '--spacing-xl': '32px',
        '--spacing-xxl': '48px',
        '--border-radius-none': '0px',
        '--border-radius-sm': '2px',
        '--border-radius-md': '4px',
        '--border-radius-lg': '8px',
        '--border-radius-full': '9999px',
        '--shadow-none': 'none',
        '--shadow-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        '--shadow-md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        '--shadow-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
    }
    
    return jsonify({'variables': css_vars}), 200


@blueprint.get('/health')
@handle_errors
def health_check():
    """Health check endpoint for the visual design service."""
    return jsonify({
        'status': 'healthy',
        'service': 'clean_visual_design',
        'version': '1.0.0'
    }), 200
