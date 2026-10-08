"""Resume Timer feature module for Flask backend."""

import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.core.db import get_engine

blueprint = Blueprint('capability_resume_timer_f65ac826', __name__)


def get_db():
    return get_engine().connect()


@blueprint.get('/api/capability_resume_timer_f65ac826/timer/state')
def get_timer_state():
    """Retrieves the current timer state to determine if the timer is paused and what the remaining time is."""
    try:
        db = get_db()
        query = text("""
            SELECT id, remaining_seconds, paused_at, is_paused, updated_at
            FROM f_f65ac826__timer_state
            ORDER BY updated_at DESC
            LIMIT 1
        """)
        result = db.execute(query).fetchone()
        
        if result is None:
            return jsonify({
                'error': 'TIMER_STATE_NOT_FOUND',
                'message': 'No timer state exists yet'
            }), 404
        
        return jsonify({
            'id': result[0],
            'remaining_seconds': result[1],
            'paused_at': result[2].isoformat() if result[2] else None,
            'is_paused': bool(result[3]),
            'updated_at': result[4].isoformat() if result[4] else None
        }), 200
        
    except SQLAlchemyError as e:
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'Failed to retrieve timer state'
        }), 500


@blueprint.post('/api/capability_resume_timer_f65ac826/timer/pause')
def save_paused_state():
    """Saves the timer state when the student pauses the timer."""
    try:
        data = request.get_json()
        
        if not data or 'remaining_seconds' not in data:
            return jsonify({
                'error': 'INVALID_REMAINING_SECONDS',
                'message': 'Remaining seconds must be between 0 and 1500'
            }), 400
        
        remaining_seconds = data['remaining_seconds']
        
        if not isinstance(remaining_seconds, int) or remaining_seconds < 0 or remaining_seconds > 1500:
            return jsonify({
                'error': 'INVALID_REMAINING_SECONDS',
                'message': 'Remaining seconds must be between 0 and 1500'
            }), 400
        
        db = get_db()
        timer_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Check if a timer state already exists
        check_query = text("""
            SELECT id FROM f_f65ac826__timer_state LIMIT 1
        """)
        existing = db.execute(check_query).fetchone()
        
        if existing:
            # Update existing timer state
            update_query = text("""
                UPDATE f_f65ac826__timer_state
                SET remaining_seconds = :remaining_seconds,
                    paused_at = :paused_at,
                    is_paused = :is_paused,
                    updated_at = :updated_at
                WHERE id = :id
            """)
            db.execute(update_query, {
                'id': existing[0],
                'remaining_seconds': remaining_seconds,
                'paused_at': now,
                'is_paused': True,
                'updated_at': now
            })
            timer_id = existing[0]
        else:
            # Insert new timer state
            insert_query = text("""
                INSERT INTO f_f65ac826__timer_state (id, remaining_seconds, paused_at, is_paused, updated_at)
                VALUES (:id, :remaining_seconds, :paused_at, :is_paused, :updated_at)
            """)
            db.execute(insert_query, {
                'id': timer_id,
                'remaining_seconds': remaining_seconds,
                'paused_at': now,
                'is_paused': True,
                'updated_at': now
            })
        
        db.commit()
        
        return jsonify({
            'id': timer_id,
            'remaining_seconds': remaining_seconds,
            'paused_at': now.isoformat(),
            'is_paused': True,
            'updated_at': now.isoformat()
        }), 200
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'Failed to save paused timer state'
        }), 500


@blueprint.post('/api/capability_resume_timer_f65ac826/timer/resume')
def clear_paused_state():
    """Updates the timer state to mark it as no longer paused when the student presses Start to resume."""
    try:
        db = get_db()
        
        # Get current timer state
        query = text("""
            SELECT id, remaining_seconds, paused_at, is_paused
            FROM f_f65ac826__timer_state
            ORDER BY updated_at DESC
            LIMIT 1
        """)
        result = db.execute(query).fetchone()
        
        if result is None:
            return jsonify({
                'error': 'TIMER_STATE_NOT_FOUND',
                'message': 'No paused timer state exists to resume'
            }), 404
        
        timer_id = result[0]
        remaining_seconds = result[1]
        paused_at = result[2]
        is_paused = bool(result[3])
        
        if not is_paused:
            return jsonify({
                'error': 'TIMER_NOT_PAUSED',
                'message': 'Timer is not currently paused'
            }), 409
        
        now = datetime.utcnow()
        
        # Update timer state to mark as not paused
        update_query = text("""
            UPDATE f_f65ac826__timer_state
            SET is_paused = :is_paused,
                updated_at = :updated_at
            WHERE id = :id
        """)
        db.execute(update_query, {
            'id': timer_id,
            'is_paused': False,
            'updated_at': now
        })
        db.commit()
        
        return jsonify({
            'id': timer_id,
            'remaining_seconds': remaining_seconds,
            'paused_at': paused_at.isoformat() if paused_at else None,
            'is_paused': False,
            'updated_at': now.isoformat()
        }), 200
        
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'Failed to resume timer'
        }), 500
