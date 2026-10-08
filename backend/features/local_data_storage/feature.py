"""
Local Data Storage Feature Module

Manages daily session state with automatic date-based reset logic.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, datetime
import uuid

blueprint = Blueprint('capability_local_data_storage_145f595e', __name__)


def get_db():
    """Get database connection from Flask app context."""
    from flask import current_app
    return current_app.config['db_engine']


@blueprint.get('/api/capability_local_data_storage_145f595e/daily-session-state')
def get_daily_session_state():
    """
    Retrieves the current daily session state when the app launches.
    
    Returns the session count and date. If no record exists, initializes a new
    state with count 0 and today's date. If the stored date differs from today,
    resets the count to 0 and updates the date to today.
    """
    try:
        engine = get_db()
        today = date.today()
        
        with engine.connect() as conn:
            # Try to fetch existing record
            result = conn.execute(
                text("SELECT id, session_count, current_date, updated_at FROM f_145f595e__daily_session_state LIMIT 1")
            )
            row = result.fetchone()
            
            if row is None:
                # No record exists, initialize new state
                new_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                conn.execute(
                    text("""
                        INSERT INTO f_145f595e__daily_session_state 
                        (id, session_count, current_date, updated_at)
                        VALUES (:id, :session_count, :current_date, :updated_at)
                    """),
                    {
                        'id': new_id,
                        'session_count': 0,
                        'current_date': today,
                        'updated_at': now
                    }
                )
                conn.commit()
                
                return jsonify({
                    'id': new_id,
                    'session_count': 0,
                    'current_date': today.isoformat(),
                    'updated_at': now.isoformat() + 'Z'
                }), 200
            
            else:
                # Record exists, check if date needs reset
                record_id = row[0]
                session_count = row[1]
                current_date = row[2]
                updated_at = row[3]
                
                # Convert current_date to date object if it's not already
                if isinstance(current_date, str):
                    current_date = date.fromisoformat(current_date)
                
                if current_date != today:
                    # Date differs, reset count to 0 and update date
                    now = datetime.utcnow()
                    
                    conn.execute(
                        text("""
                            UPDATE f_145f595e__daily_session_state
                            SET session_count = :session_count,
                                current_date = :current_date,
                                updated_at = :updated_at
                            WHERE id = :id
                        """),
                        {
                            'id': record_id,
                            'session_count': 0,
                            'current_date': today,
                            'updated_at': now
                        }
                    )
                    conn.commit()
                    
                    return jsonify({
                        'id': record_id,
                        'session_count': 0,
                        'current_date': today.isoformat(),
                        'updated_at': now.isoformat() + 'Z'
                    }), 200
                
                else:
                    # Date matches, return existing state
                    if isinstance(updated_at, datetime):
                        updated_at_str = updated_at.isoformat() + 'Z'
                    else:
                        updated_at_str = str(updated_at)
                    
                    return jsonify({
                        'id': record_id,
                        'session_count': session_count,
                        'current_date': current_date.isoformat(),
                        'updated_at': updated_at_str
                    }), 200
    
    except SQLAlchemyError as e:
        return jsonify({
            'error': 'STORAGE_ERROR',
            'message': 'Failed to read or initialize daily session state'
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'STORAGE_ERROR',
            'message': 'Failed to read or initialize daily session state'
        }), 500


@blueprint.post('/api/capability_local_data_storage_145f595e/daily-session-state/increment')
def increment_session_count():
    """
    Increments the daily session count by 1 after a session completes.
    
    Persists the updated count to storage immediately. If the stored date
    differs from today, resets the count to 1 and updates the date to today.
    """
    try:
        engine = get_db()
        today = date.today()
        
        with engine.connect() as conn:
            # Fetch existing record
            result = conn.execute(
                text("SELECT id, session_count, current_date FROM f_145f595e__daily_session_state LIMIT 1")
            )
            row = result.fetchone()
            
            if row is None:
                # No record exists, return error
                return jsonify({
                    'error': 'STATE_NOT_FOUND',
                    'message': 'Daily session state record does not exist; call GET first to initialize'
                }), 404
            
            record_id = row[0]
            session_count = row[1]
            current_date = row[2]
            
            # Convert current_date to date object if it's not already
            if isinstance(current_date, str):
                current_date = date.fromisoformat(current_date)
            
            now = datetime.utcnow()
            
            if current_date != today:
                # Date differs, reset count to 1 and update date
                new_count = 1
                
                conn.execute(
                    text("""
                        UPDATE f_145f595e__daily_session_state
                        SET session_count = :session_count,
                            current_date = :current_date,
                            updated_at = :updated_at
                        WHERE id = :id
                    """),
                    {
                        'id': record_id,
                        'session_count': new_count,
                        'current_date': today,
                        'updated_at': now
                    }
                )
                conn.commit()
                
                return jsonify({
                    'id': record_id,
                    'session_count': new_count,
                    'current_date': today.isoformat(),
                    'updated_at': now.isoformat() + 'Z'
                }), 200
            
            else:
                # Date matches, increment count
                new_count = session_count + 1
                
                conn.execute(
                    text("""
                        UPDATE f_145f595e__daily_session_state
                        SET session_count = :session_count,
                            updated_at = :updated_at
                        WHERE id = :id
                    """),
                    {
                        'id': record_id,
                        'session_count': new_count,
                        'updated_at': now
                    }
                )
                conn.commit()
                
                return jsonify({
                    'id': record_id,
                    'session_count': new_count,
                    'current_date': today.isoformat(),
                    'updated_at': now.isoformat() + 'Z'
                }), 200
    
    except SQLAlchemyError as e:
        return jsonify({
            'error': 'STORAGE_ERROR',
            'message': 'Failed to increment and save session count'
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'STORAGE_ERROR',
            'message': 'Failed to increment and save session count'
        }), 500
