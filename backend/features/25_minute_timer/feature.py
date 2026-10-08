"""
25-Minute Timer Feature Module

This module implements a fixed-duration countdown timer set to 25 minutes
that students use to time their study sessions.
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
import uuid
import os

blueprint = Blueprint('capability_25_minute_timer_f4c5a58c', __name__)

def get_db_connection():
    """Get database connection using SQLAlchemy engine."""
    database_url = os.environ.get('DATABASE_URL', 'mysql+pymysql://user:password@localhost/db')
    engine = create_engine(database_url, pool_pre_ping=True)
    return engine.connect()


@blueprint.post('/api/capability_25_minute_timer_f4c5a58c/sessions')
def record_completed_session():
    """
    Records a completed 25-minute study session when the timer reaches 0:00,
    creating a permanent record with completion timestamp and duration.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'INVALID_REQUEST',
                'message': 'Request body must be valid JSON'
            }), 400
        
        # Validate required fields
        if 'completed_at' not in data:
            return jsonify({
                'error': 'INVALID_TIMESTAMP',
                'message': 'Completed_at must be a valid ISO 8601 timestamp'
            }), 400
        
        if 'duration_minutes' not in data:
            return jsonify({
                'error': 'INVALID_DURATION',
                'message': 'Duration must be exactly 25 minutes'
            }), 400
        
        # Validate duration is exactly 25
        duration_minutes = data['duration_minutes']
        if duration_minutes != 25:
            return jsonify({
                'error': 'INVALID_DURATION',
                'message': 'Duration must be exactly 25 minutes'
            }), 400
        
        # Validate and parse completed_at timestamp
        completed_at_str = data['completed_at']
        try:
            # Parse ISO 8601 timestamp
            completed_at = datetime.fromisoformat(completed_at_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return jsonify({
                'error': 'INVALID_TIMESTAMP',
                'message': 'Completed_at must be a valid ISO 8601 timestamp'
            }), 400
        
        # Generate UUID for the session
        session_id = str(uuid.uuid4())
        
        # Insert into database
        conn = get_db_connection()
        try:
            query = text("""
                INSERT INTO f_f4c5a58c__study_sessions 
                (id, completed_at, duration_minutes)
                VALUES (:id, :completed_at, :duration_minutes)
            """)
            
            conn.execute(query, {
                'id': session_id,
                'completed_at': completed_at,
                'duration_minutes': duration_minutes
            })
            conn.commit()
            
            return jsonify({
                'id': session_id,
                'completed_at': completed_at.isoformat(),
                'duration_minutes': duration_minutes
            }), 201
            
        except SQLAlchemyError as e:
            conn.rollback()
            return jsonify({
                'error': 'DATABASE_ERROR',
                'message': 'Failed to record session'
            }), 500
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'error': 'DATABASE_ERROR',
            'message': 'Failed to record session'
        }), 500


@blueprint.get('/api/capability_25_minute_timer_f4c5a58c/sessions/daily-count')
def get_daily_session_count():
    """
    Retrieves the count of completed study sessions for a specific date
    to display the daily session counter.
    """
    try:
        # Get date parameter from query string, default to today
        date_str = request.args.get('date')
        
        if date_str:
            try:
                # Parse ISO 8601 date (YYYY-MM-DD)
                target_date = date.fromisoformat(date_str)
            except ValueError:
                return jsonify({
                    'error': 'INVALID_DATE',
                    'message': 'Date must be a valid ISO 8601 date (YYYY-MM-DD)'
                }), 400
        else:
            # Default to today
            target_date = date.today()
        
        # Query database for count of sessions on the target date
        conn = get_db_connection()
        try:
            query = text("""
                SELECT COUNT(*) as count
                FROM f_f4c5a58c__study_sessions
                WHERE DATE(completed_at) = :target_date
            """)
            
            result = conn.execute(query, {'target_date': target_date})
            row = result.fetchone()
            count = row[0] if row else 0
            
            return jsonify({
                'date': target_date.isoformat(),
                'count': count
            }), 200
            
        except SQLAlchemyError as e:
            return jsonify({
                'error': 'DATABASE_ERROR',
                'message': 'Failed to retrieve session count'
            }), 500
        finally:
            conn.close()
            
    except Exception as e:
        return jsonify({
            'error': 'DATABASE_ERROR',
            'message': 'Failed to retrieve session count'
        }), 500
