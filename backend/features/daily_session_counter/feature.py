"""Daily Session Counter feature module for tracking completed focus sessions."""

import uuid
from datetime import datetime, timezone as dt_timezone
from flask import Blueprint, request, jsonify
from sqlalchemy import text, func
from sqlalchemy.exc import SQLAlchemyError
import pytz

# Create Blueprint
blueprint = Blueprint('capability_daily_session_counter_7a9d9848', __name__)


def get_db_connection():
    """Get database connection from Flask app context."""
    from flask import current_app
    return current_app.config['db_engine'].connect()


@blueprint.post('/api/capability_daily_session_counter_7a9d9848/sessions/complete')
def record_completed_session():
    """
    Records a completed 25-minute focus session when the timer reaches 0:00.
    
    Stores the completion timestamp to enable daily count calculation.
    """
    try:
        data = request.get_json()
        
        if not data or 'completed_at' not in data:
            return jsonify({
                'code': 'INVALID_TIMESTAMP',
                'message': 'completed_at must be a valid ISO 8601 timestamp'
            }), 400
        
        completed_at_str = data['completed_at']
        
        # Validate ISO 8601 timestamp
        try:
            completed_at = datetime.fromisoformat(completed_at_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return jsonify({
                'code': 'INVALID_TIMESTAMP',
                'message': 'completed_at must be a valid ISO 8601 timestamp'
            }), 400
        
        # Generate UUID for the session
        session_id = str(uuid.uuid4())
        
        # Insert into database
        conn = get_db_connection()
        try:
            query = text("""
                INSERT INTO f_7a9d9848__completed_sessions (id, completed_at)
                VALUES (:id, :completed_at)
            """)
            conn.execute(query, {
                'id': session_id,
                'completed_at': completed_at
            })
            conn.commit()
        except SQLAlchemyError as e:
            conn.rollback()
            return jsonify({
                'code': 'STORAGE_ERROR',
                'message': 'Failed to record completed session'
            }), 500
        finally:
            conn.close()
        
        # Return response
        return jsonify({
            'id': session_id,
            'completed_at': completed_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 'STORAGE_ERROR',
            'message': 'Failed to record completed session'
        }), 500


@blueprint.get('/api/capability_daily_session_counter_7a9d9848/sessions/today/count')
def get_daily_session_count():
    """
    Retrieves the count of completed sessions for the current calendar day.
    
    Queries sessions with today's date, returning 0 on first launch or at the start of a new day.
    """
    try:
        # Get timezone from query parameters
        tz_str = request.args.get('timezone', 'UTC')
        
        # Validate timezone
        try:
            tz = pytz.timezone(tz_str)
        except pytz.exceptions.UnknownTimeZoneError:
            return jsonify({
                'code': 'INVALID_TIMEZONE',
                'message': 'timezone must be a valid IANA timezone identifier'
            }), 400
        
        # Get current date in the specified timezone
        now_in_tz = datetime.now(tz)
        today_date = now_in_tz.date()
        
        # Calculate start and end of day in UTC for database query
        start_of_day = tz.localize(datetime.combine(today_date, datetime.min.time()))
        end_of_day = tz.localize(datetime.combine(today_date, datetime.max.time()))
        
        start_of_day_utc = start_of_day.astimezone(dt_timezone.utc)
        end_of_day_utc = end_of_day.astimezone(dt_timezone.utc)
        
        # Query database for count
        conn = get_db_connection()
        try:
            query = text("""
                SELECT COUNT(*) as count
                FROM f_7a9d9848__completed_sessions
                WHERE completed_at >= :start_time AND completed_at <= :end_time
            """)
            result = conn.execute(query, {
                'start_time': start_of_day_utc,
                'end_time': end_of_day_utc
            })
            row = result.fetchone()
            count = row[0] if row else 0
        except SQLAlchemyError as e:
            return jsonify({
                'code': 'STORAGE_ERROR',
                'message': 'Failed to retrieve session count'
            }), 500
        finally:
            conn.close()
        
        # Return response
        return jsonify({
            'count': count,
            'date': today_date.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 'STORAGE_ERROR',
            'message': 'Failed to retrieve session count'
        }), 500
