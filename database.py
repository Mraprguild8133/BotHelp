import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict

logger = logging.getLogger(__name__)

class AnimeBotDatabase:
    def __init__(self, db_name: str = "anime_bot.db"):
        self.db_name = db_name
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize database tables."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # User levels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_levels (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                messages_count INTEGER DEFAULT 0,
                last_message_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Warnings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chat_id INTEGER,
                warned_by INTEGER,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Mutes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                chat_id INTEGER,
                muted_by INTEGER,
                duration_hours INTEGER,
                unmute_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                warnings_count INTEGER DEFAULT 0,
                mutes_count INTEGER DEFAULT 0,
                kicks_count INTEGER DEFAULT 0,
                bans_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    # === User Level Methods ===
    def get_user_level(self, user_id: int) -> Tuple[int, int]:
        """Get user's level and XP."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT level, xp FROM user_levels WHERE user_id = ?', 
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result['level'], result['xp']
        return 1, 0
    
    def add_user_xp(self, user_id: int, username: str, first_name: str, xp: int) -> Tuple[int, int, bool]:
        """Add XP to user and check for level up."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get or create user
        cursor.execute(
            'SELECT level, xp FROM user_levels WHERE user_id = ?', 
            (user_id,)
        )
        result = cursor.fetchone()
        
        current_time = datetime.now()
        
        if result:
            current_level = result['level']
            current_xp = result['xp']
            new_xp = current_xp + xp
            new_level = self._calculate_level(new_xp)
            leveled_up = new_level > current_level
            
            cursor.execute('''
                UPDATE user_levels 
                SET xp = ?, level = ?, username = ?, first_name = ?, 
                    messages_count = messages_count + 1, last_message_time = ?
                WHERE user_id = ?
            ''', (new_xp, new_level, username, first_name, current_time, user_id))
        else:
            new_level = 1
            new_xp = xp
            leveled_up = False
            cursor.execute('''
                INSERT INTO user_levels 
                (user_id, username, first_name, xp, level, messages_count, last_message_time)
                VALUES (?, ?, ?, ?, ?, 1, ?)
            ''', (user_id, username, first_name, new_xp, new_level, current_time))
        
        conn.commit()
        conn.close()
        return new_level, new_xp, leveled_up
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate level based on XP."""
        level = 1
        required_xp = 100
        
        while xp >= required_xp:
            level += 1
            xp -= required_xp
            required_xp = int(required_xp * 1.5)
        
        return level
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users by level."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, first_name, level, xp, messages_count 
            FROM user_levels 
            ORDER BY level DESC, xp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        conn.close()
        return results
    
    def get_user_rank(self, user_id: int) -> int:
        """Get user's rank in the leaderboard."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as rank
            FROM user_levels 
            WHERE (level * 1000000 + xp) > (
                SELECT level * 1000000 + xp 
                FROM user_levels 
                WHERE user_id = ?
            )
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        return result['rank'] + 1 if result else 1
    
    # === Warning System Methods ===
    def add_warning(self, user_id: int, chat_id: int, warned_by: int, reason: str = "No reason provided"):
        """Add a warning for user."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO warnings (user_id, chat_id, warned_by, reason)
            VALUES (?, ?, ?, ?)
        ''', (user_id, chat_id, warned_by, reason))
        
        # Update user stats
        cursor.execute('''
            INSERT OR REPLACE INTO user_stats (user_id, warnings_count, last_updated)
            VALUES (?, COALESCE((SELECT warnings_count FROM user_stats WHERE user_id = ?), 0) + 1, ?)
        ''', (user_id, user_id, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_user_warnings(self, user_id: int, chat_id: int) -> List[Dict]:
        """Get all warnings for user in specific chat."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM warnings 
            WHERE user_id = ? AND chat_id = ?
            ORDER BY created_at DESC
        ''', (user_id, chat_id))
        
        warnings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return warnings
    
    def get_warning_count(self, user_id: int, chat_id: int) -> int:
        """Get warning count for user in specific chat."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM warnings 
            WHERE user_id = ? AND chat_id = ?
        ''', (user_id, chat_id))
        
        result = cursor.fetchone()
        conn.close()
        return result['count'] if result else 0
    
    def clear_warnings(self, user_id: int, chat_id: int):
        """Clear all warnings for user in specific chat."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM warnings 
            WHERE user_id = ? AND chat_id = ?
        ''', (user_id, chat_id))
        
        conn.commit()
        conn.close()
    
    # === Mute System Methods ===
    def add_mute(self, user_id: int, chat_id: int, muted_by: int, duration_hours: int):
        """Add mute record for user."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        unmute_time = datetime.now() + timedelta(hours=duration_hours)
        
        cursor.execute('''
            INSERT INTO mutes (user_id, chat_id, muted_by, duration_hours, unmute_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, chat_id, muted_by, duration_hours, unmute_time))
        
        # Update user stats
        cursor.execute('''
            INSERT OR REPLACE INTO user_stats (user_id, mutes_count, last_updated)
            VALUES (?, COALESCE((SELECT mutes_count FROM user_stats WHERE user_id = ?), 0) + 1, ?)
        ''', (user_id, user_id, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_active_mutes(self, chat_id: int) -> List[Dict]:
        """Get all active mutes in chat."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, u.username, u.first_name
            FROM mutes m
            LEFT JOIN user_levels u ON m.user_id = u.user_id
            WHERE m.chat_id = ? AND m.unmute_time > ?
        ''', (chat_id, datetime.now()))
        
        mutes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return mutes
    
    def remove_mute(self, user_id: int, chat_id: int):
        """Remove mute record for user."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM mutes 
            WHERE user_id = ? AND chat_id = ?
        ''', (user_id, chat_id))
        
        conn.commit()
        conn.close()
    
    # === Statistics Methods ===
    def get_user_stats(self, user_id: int) -> Dict:
        """Get comprehensive user statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get level info
        cursor.execute('SELECT * FROM user_levels WHERE user_id = ?', (user_id,))
        level_info = cursor.fetchone()
        
        # Get warning stats
        cursor.execute('SELECT COUNT(*) as total_warnings FROM warnings WHERE user_id = ?', (user_id,))
        warning_stats = cursor.fetchone()
        
        # Get other stats
        cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
        user_stats = cursor.fetchone()
        
        conn.close()
        
        stats = {}
        if level_info:
            stats.update(dict(level_info))
        if warning_stats:
            stats['total_warnings'] = warning_stats['total_warnings']
        if user_stats:
            stats.update(dict(user_stats))
        
        return stats
    
    def get_chat_stats(self, chat_id: int) -> Dict:
        """Get chat statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total users in chat
        cursor.execute('SELECT COUNT(DISTINCT user_id) as total_users FROM warnings WHERE chat_id = ?', (chat_id,))
        total_users = cursor.fetchone()['total_users']
        
        # Total warnings in chat
        cursor.execute('SELECT COUNT(*) as total_warnings FROM warnings WHERE chat_id = ?', (chat_id,))
        total_warnings = cursor.fetchone()['total_warnings']
        
        # Active mutes
        cursor.execute('SELECT COUNT(*) as active_mutes FROM mutes WHERE chat_id = ? AND unmute_time > ?', 
                      (chat_id, datetime.now()))
        active_mutes = cursor.fetchone()['active_mutes']
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_warnings': total_warnings,
            'active_mutes': active_mutes
        }
    
    # === Cleanup Methods ===
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Clean old warnings
        cursor.execute('DELETE FROM warnings WHERE created_at < ?', (cutoff_date,))
        
        # Clean expired mutes
        cursor.execute('DELETE FROM mutes WHERE unmute_time < ?', (datetime.now(),))
        
        conn.commit()
        conn.close()
        logger.info(f"Cleaned up data older than {days} days")
