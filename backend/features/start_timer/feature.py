"""
Flask Blueprint module for Start Timer feature.
Implements timer start, pause, and state retrieval functionality.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime, timezone
import uuid

from backend.core.db import get_engine

blueprint = Blueprint('capability_start_timer_a5aab8dc', __name__)
db_session = scoped_session(sessionmaker(bind=get_engine(), future=True))


@blueprint.teardown_request
def remove_db_session(_exception=None):
    db_session.remove()

# Constants
DEFAULT_TIMER_SECONDS = 1500  # 25 minutes
TABLE_NAME = 'f_a5aab8dc__timer_session'


def get_active_session():
    """
    Retrieves the most recent timer session from the database.
    Returns None if no session exists.
    """
    query = text(f"""
        SELECT id, remaining_seconds, is_running, started_at, created_at, updated_at
        FROM {TABLE_NAME}
        ORDER BY updated_at DESC
        LIMIT 1
    """)
    result = db_session.execute(query)
    row = result.fetchone()
    if row:
        return {
            'id': row[0],
            'remaining_seconds': row[1],
            'is_running': bool(row[2]),
            'started_at': row[3],
            'created_at': row[4],
            'updated_at': row[5]
        }
    return None


def calculate_remaining_seconds(session):
    """
    Calculates the actual remaining seconds for a running timer.
    If the timer is running, subtracts elapsed time from remaining_seconds.
    """
    if not session['is_running'] or session['started_at'] is None:
        return session['remaining_seconds']
    
    started_at = session['started_at']
    if isinstance(started_at, str):
        started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
    elif started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    elapsed_seconds = int((now - started_at).total_seconds())
    remaining = max(0, session['remaining_seconds'] - elapsed_seconds)
    
    return remaining


@blueprint.route('/api/capability_start_timer_a5aab8dc/timer/state', methods=['GET'])
def get_timer_state():
    """
    Retrieves the current timer session state to display on the main screen,
    including remaining time and running status. Returns default 25:00 state
    if no active session exists.
    """
    try:
        session = get_active_session()
        
        if session is None:
            # Return default state
            return jsonify({
                'id': None,
                'remaining_seconds': DEFAULT_TIMER_SECONDS,
                'is_running': False,
                'started_at': None
            }), 200
        
        # Calculate actual remaining seconds if running
        remaining_seconds = calculate_remaining_seconds(session)
        
        response = {
            'id': session['id'],
            'remaining_seconds': remaining_seconds,
            'is_running': session['is_running']
        }
        
        if session['is_running'] and session['started_at']:
            started_at = session['started_at']
            if isinstance(started_at, datetime):
                response['started_at'] = started_at.isoformat()
            else:
                response['started_at'] = started_at
        else:
            response['started_at'] = None
        
        return jsonify(response), 200
        
    except SQLAlchemyError as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to retrieve timer state'
        }), 500
    except Exception as e:
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to retrieve timer state'
        }), 500


@blueprint.route('/api/capability_start_timer_a5aab8dc/timer/start', methods=['POST'])
def start_timer():
    """
    Begins a new 25-minute countdown from 25:00 or resumes an existing paused
    session from its current remaining time. Creates or updates the timer_session
    record with is_running=true and started_at timestamp.
    """
    try:
        session = get_active_session()
        now = datetime.now(timezone.utc)
        
        if session and session['is_running']:
            return jsonify({
                'code': 'ALREADY_RUNNING',
                'message': 'Timer is already running'
            }), 400
        
        if session is None:
            # Create new session starting at 25:00
            session_id = str(uuid.uuid4())
            remaining_seconds = DEFAULT_TIMER_SECONDS
            
            insert_query = text(f"""
                INSERT INTO {TABLE_NAME} (id, remaining_seconds, is_running, started_at)
                VALUES (:id, :remaining_seconds, :is_running, :started_at)
            """)
            
            db_session.execute(insert_query, {
                'id': session_id,
                'remaining_seconds': remaining_seconds,
                'is_running': True,
                'started_at': now
            })
            db_session.commit()
            
        else:
            # Resume existing paused session
            session_id = session['id']
            remaining_seconds = session['remaining_seconds']
            
            update_query = text(f"""
                UPDATE {TABLE_NAME}
                SET is_running = :is_running, started_at = :started_at
                WHERE id = :id
            """)
            
            db_session.execute(update_query, {
                'id': session_id,
                'is_running': True,
                'started_at': now
            })
            db_session.commit()
        
        return jsonify({
            'id': session_id,
            'remaining_seconds': remaining_seconds,
            'is_running': True,
            'started_at': now.isoformat()
        }), 200
        
    except SQLAlchemyError as e:
        db_session.rollback()
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to start timer'
        }), 500
    except Exception as e:
        db_session.rollback()
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to start timer'
        }), 500


@blueprint.route('/api/capability_start_timer_a5aab8dc/timer/pause', methods=['POST'])
def pause_timer():
    """
    Pauses the running timer by calculating elapsed time since started_at,
    updating remaining_seconds, setting is_running=false, and clearing started_at.
    Enables resume from current time.
    """
    try:
        session = get_active_session()
        
        if session is None:
            return jsonify({
                'code': 'NO_ACTIVE_SESSION',
                'message': 'No active timer session found'
            }), 404
        
        if not session['is_running']:
            return jsonify({
                'code': 'NOT_RUNNING',
                'message': 'Timer is not running'
            }), 400
        
        # Calculate remaining seconds after pause
        remaining_seconds = calculate_remaining_seconds(session)
        
        # Update session to paused state
        update_query = text(f"""
            UPDATE {TABLE_NAME}
            SET remaining_seconds = :remaining_seconds,
                is_running = :is_running,
                started_at = NULL
            WHERE id = :id
        """)
        
        db_session.execute(update_query, {
            'id': session['id'],
            'remaining_seconds': remaining_seconds,
            'is_running': False
        })
        db_session.commit()
        
        return jsonify({
            'id': session['id'],
            'remaining_seconds': remaining_seconds,
            'is_running': False,
            'started_at': None
        }), 200
        
    except SQLAlchemyError as e:
        db_session.rollback()
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to pause timer'
        }), 500
    except Exception as e:
        db_session.rollback()
        return jsonify({
            'code': 'INTERNAL_ERROR',
            'message': 'Failed to pause timer'
        }), 500
