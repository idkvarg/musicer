from variables import *
import sqlite3 # to use sqlite3 database

# Create a SQLite database and table
def create_database(db_name="music.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS track_info (
            spotify_track_id TEXT PRIMARY KEY,
            telegram_audio_id TEXT,
            telegram_channel_id INTEGER,
            message_id INTEGER,
            s3_status INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Function to fetch a telegram_audio_id by spotify_track_id
def get_telegram_audio_id(spotify_track_id, db_name="music.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        SELECT telegram_audio_id FROM track_info WHERE spotify_track_id = ?
    ''', (spotify_track_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# function to fetch telegram_channel_id by spotify_track_id
def get_telegram_channel_id(spotify_track_id, db_name="music.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        SELECT telegram_channel_id FROM track_info WHERE spotify_track_id = ?
    ''', (spotify_track_id))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Function to add or update data in the database
def add_or_update_track_info(spotify_track_id, telegram_audio_id, telegram_channel_id, message_id, db_name="music.db"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO track_info (spotify_track_id, telegram_audio_id, telegram_channel_id, message_id, s3_status)
        VALUES (?, ?, ?, ?, 0)
    ''', (spotify_track_id, telegram_audio_id, telegram_channel_id, message_id))
    conn.commit()
    conn.close()

def delete_track(spotify_track_id, db_name="music.db"):
    """
    Delete an entry from the track_info table by its spotify_track_id if it exists.
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        DELETE FROM track_info WHERE spotify_track_id = ?
    ''', (spotify_track_id,))
    conn.commit()
    conn.close()

def update_s3_status(spotify_track_id, s3_status, db_name="music.db"):
    """
    Update the s3_status for a specific track by its spotify_track_id.
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        UPDATE track_info SET s3_status = ? WHERE spotify_track_id = ?
    ''', (int(s3_status), spotify_track_id))
    conn.commit()
    conn.close()

def get_all_tracks_for_backup(start_index=0, db_name="music.db"):
    """
    Get all tracks from database starting from a specific index.
    Returns list of tuples (index, spotify_track_id, telegram_audio_id)
    where index is the row number (0-based) for resume functionality.
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        SELECT spotify_track_id, telegram_audio_id FROM track_info 
        WHERE telegram_audio_id IS NOT NULL AND s3_status = 0 AND (telegram_channel_id IS NULL OR telegram_channel_id != ?)
        ORDER BY spotify_track_id
    ''', (SP11_CHANNEL_ID,))
    results = c.fetchall()
    conn.close()
    
    # Add index to each result and filter from start_index
    indexed_results = [(i, row[0], row[1]) for i, row in enumerate(results) if i >= start_index]
    return indexed_results

def get_total_tracks_count(db_name="music.db"):
    """
    Get total count of tracks that need backup (s3_status = 0).
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        SELECT COUNT(*) FROM track_info 
        WHERE telegram_audio_id IS NOT NULL AND s3_status = 0
    ''')
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def get_start_index_by_letters(first_letters, db_name="music.db"):
    """
    Calculate start index based on first letters of track_id.
    Returns the index of the first track starting with those letters,
    or the index of the first track that comes after alphabetically if no exact match.
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        SELECT spotify_track_id FROM track_info 
        WHERE telegram_audio_id IS NOT NULL AND s3_status = 0 AND (telegram_channel_id IS NULL OR telegram_channel_id != ?)
        ORDER BY spotify_track_id
    ''', (SP11_CHANNEL_ID,))
    results = c.fetchall()
    conn.close()
    
    # Find the first track that starts with the given letters or comes after
    for i, (track_id,) in enumerate(results):
        if track_id >= first_letters:
            return i
    
    # If no track found, return the total count (end of list)
    return len(results)