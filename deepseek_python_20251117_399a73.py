import logging
import random
import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from telegram import Update, ChatMember, ChatPermissions
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackContext, ChatMemberHandler
)

# === CONFIGURATION ===
class Config:
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    ADMIN_IDS = [123456789]
    DATABASE_NAME = "anime_bot.db"
    MAX_WARNINGS = 3
    MUTE_DURATION_HOURS = 1
    WARNING_EXPIRE_HOURS = 24
    ANTI_SPAM_COOLDOWN = 2
    
    WELCOME_IMAGE_URLS = [
        "https://i.imgur.com/8SqjK2v.png",
        "https://i.imgur.com/9X8qjK2.png",
    ]
    ENABLE_WELCOME_IMAGE = True
    WELCOME_IMAGE_CAPTION = True
    
    ANIME_QUOTES = [
        "Believe in the me that believes in you! - Kamina (Gurren Lagann)",
        "People's dreams never end! - Marshall D. Teach (One Piece)",
    ]
    
    ANIME_WELCOME_MESSAGES = [
        "Welcome {user}! You've entered the world of anime! 🌸",
        "Konichiwa {user}! Ready for some anime adventures? ✨",
    ]
    
    ANIME_CHARACTERS = {
        "naruto": {
            "name": "Naruto Uzumaki", "series": "Naruto",
            "image": "https://i.imgur.com/naruto_image.jpg",
            "quote": "I'm not gonna run away, I never go back on my word!",
            "description": "A shinobi of Konohagakure's Uzumaki clan."
        }
    }
    
    LEVEL_CONFIG = {
        "ENABLE_LEVEL_SYSTEM": True,
        "XP_PER_MESSAGE": 5,
        "XP_COOLDOWN": 60,
        "LEVEL_UP_MESSAGES": [
            "🎉 {user} leveled up to level {level}! Sugoi!",
        ]
    }
    
    RESPONSES = {
        "no_permission": "❌ You need to be an admin to use this command!",
        "no_user_mentioned": "❌ Please mention a user!\nUsage: {usage}",
        "user_not_found": "❌ Could not find the mentioned user!",
        "command_failed": "❌ Failed to execute command: {error}",
        "welcome_bot": "Arigatou for adding me! I'll protect this anime community! 🌸\nUse /help to see my commands!",
        "spam_warning": "{user} please don't spam! 🚫",
        "image_send_failed": "Failed to send image, sending text instead."
    }

config = Config()

# === DATABASE CLASS ===
class AnimeBotDatabase:
    def __init__(self, db_name: str = "anime_bot.db"):
        self.db_name = db_name
        self._init_database()
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_levels (
                user_id INTEGER PRIMARY KEY,
                username TEXT, first_name TEXT,
                xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1,
                messages_count INTEGER DEFAULT 0,
                last_message_time TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, chat_id INTEGER,
                warned_by INTEGER, reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, chat_id INTEGER,
                muted_by INTEGER, duration_hours INTEGER,
                unmute_time TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_level(self, user_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT level, xp FROM user_levels WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return (result['level'], result['xp']) if result else (1, 0)
    
    def add_user_xp(self, user_id: int, username: str, first_name: str, xp: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT level, xp FROM user_levels WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        current_time = datetime.now()
        
        if result:
            current_level, current_xp = result['level'], result['xp']
            new_xp = current_xp + xp
            new_level = self._calculate_level(new_xp)
            leveled_up = new_level > current_level
            
            cursor.execute('''
                UPDATE user_levels SET xp=?, level=?, username=?, first_name=?, 
                messages_count=messages_count+1, last_message_time=? WHERE user_id=?
            ''', (new_xp, new_level, username, first_name, current_time, user_id))
        else:
            new_level, new_xp = 1, xp
            leveled_up = False
            cursor.execute('''
                INSERT INTO user_levels (user_id, username, first_name, xp, level, messages_count, last_message_time)
                VALUES (?, ?, ?, ?, ?, 1, ?)
            ''', (user_id, username, first_name, new_xp, new_level, current_time))
        
        conn.commit()
        conn.close()
        return new_level, new_xp, leveled_up
    
    def _calculate_level(self, xp: int):
        level, required_xp = 1, 100
        while xp >= required_xp:
            level += 1
            xp -= required_xp
            required_xp = int(required_xp * 1.5)
        return level
    
    def get_leaderboard(self, limit: int = 10):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, first_name, level, xp FROM user_levels ORDER BY level DESC, xp DESC LIMIT ?', (limit,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_user_rank(self, user_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as rank FROM user_levels 
            WHERE (level * 1000000 + xp) > (SELECT level * 1000000 + xp FROM user_levels WHERE user_id = ?)
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result['rank'] + 1 if result else 1
    
    def add_warning(self, user_id: int, chat_id: int, warned_by: int, reason: str = "No reason"):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO warnings (user_id, chat_id, warned_by, reason) VALUES (?, ?, ?, ?)', 
                      (user_id, chat_id, warned_by, reason))
        conn.commit()
        conn.close()
    
    def get_warning_count(self, user_id: int, chat_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM warnings WHERE user_id=? AND chat_id=?', (user_id, chat_id))
        result = cursor.fetchone()
        conn.close()
        return result['count'] if result else 0
    
    def clear_warnings(self, user_id: int, chat_id: int):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM warnings WHERE user_id=? AND chat_id=?', (user_id, chat_id))
        conn.commit()
        conn.close()
    
    def cleanup_old_data(self, days: int = 30):
        conn = self._get_connection()
        cursor = conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        cursor.execute('DELETE FROM warnings WHERE created_at < ?', (cutoff_date,))
        cursor.execute('DELETE FROM mutes WHERE unmute_time < ?', (datetime.now(),))
        conn.commit()
        conn.close()

# === MAIN BOT CLASS ===
class AnimeGroupManager:
    def __init__(self):
        self.db = AnimeBotDatabase(config.DATABASE_NAME)
        self.last_xp_gain = {}
        self.start_time = datetime.now()
    
    # ... [Include all the methods from the previous bot.py here]
    # Copy all the methods from the previous corrected bot.py version

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    application = Application.builder().token(config.BOT_TOKEN).build()
    manager = AnimeGroupManager()
    
    # Add all handlers
    application.add_handler(CommandHandler("start", manager.start))
    application.add_handler(CommandHandler("help", manager.help_command))
    application.add_handler(CommandHandler("quote", manager.send_quote))
    application.add_handler(CommandHandler("rules", manager.show_rules))
    application.add_handler(CommandHandler("level", manager.level_command))
    application.add_handler(CommandHandler("leaderboard", manager.leaderboard_command))
    application.add_handler(CommandHandler("character", manager.character_command))
    application.add_handler(CommandHandler("stats", manager.stats_command))
    application.add_handler(CommandHandler("userstats", manager.userstats_command))
    application.add_handler(CommandHandler("warn", manager.warn_user))
    application.add_handler(CommandHandler("warnings", manager.warnings_command))
    application.add_handler(CommandHandler("mute", manager.mute_user))
    application.add_handler(CommandHandler("unmute", manager.unmute_user))
    application.add_handler(CommandHandler("ban", manager.ban_user))
    application.add_handler(CommandHandler("kick", manager.kick_user))
    
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, manager.welcome_new_member))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manager.handle_level_system))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manager.anti_spam))
    
    asyncio.get_event_loop().create_task(manager.run_cleanup_tasks())
    
    logger.info("🌸 Anime Guardian Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()