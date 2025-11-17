import logging
import random
import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

from telegram import (
    Update, ChatMember, ChatPermissions, InputMediaPhoto,
    Poll, Message
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackContext, ChatMemberHandler, PollHandler
)

from config import config

# Set up logging
logging.basicConfig(
    format=config.LOG_FORMAT,
    level=getattr(logging, config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

class UserLevel:
    def __init__(self):
        self.conn = sqlite3.connect('user_levels.db', check_same_thread=False)
        self._create_table()
    
    def _create_table(self):
        """Create user levels table if not exists."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_levels (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                messages_count INTEGER DEFAULT 0,
                last_message_time TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def get_user_level(self, user_id: int) -> Tuple[int, int]:
        """Get user's level and XP."""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT level, xp FROM user_levels WHERE user_id = ?', 
            (user_id,)
        )
        result = cursor.fetchone()
        if result:
            return result[0], result[1]
        return 1, 0
    
    def add_xp(self, user_id: int, username: str, xp: int) -> Tuple[int, int, bool]:
        """Add XP to user and check for level up."""
        cursor = self.conn.cursor()
        
        # Get current level and XP
        cursor.execute(
            'SELECT level, xp FROM user_levels WHERE user_id = ?', 
            (user_id,)
        )
        result = cursor.fetchone()
        
        if result:
            current_level, current_xp = result
            new_xp = current_xp + xp
            new_level = self._calculate_level(new_xp)
            leveled_up = new_level > current_level
            
            cursor.execute('''
                UPDATE user_levels 
                SET xp = ?, level = ?, username = ?, messages_count = messages_count + 1,
                    last_message_time = ?
                WHERE user_id = ?
            ''', (new_xp, new_level, username, datetime.now(), user_id))
        else:
            new_level = 1
            new_xp = xp
            leveled_up = False
            cursor.execute('''
                INSERT INTO user_levels (user_id, username, xp, level, messages_count, last_message_time)
                VALUES (?, ?, ?, ?, 1, ?)
            ''', (user_id, username, new_xp, new_level, datetime.now()))
        
        self.conn.commit()
        return new_level, new_xp, leveled_up
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate level based on XP."""
        return max(1, int((xp / 100) ** 0.5))
    
    def get_leaderboard(self, limit: int = 10) -> List[Tuple]:
        """Get top users by level."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT username, level, xp, messages_count 
            FROM user_levels 
            ORDER BY level DESC, xp DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

class AnimeQuiz:
    def __init__(self):
        self.questions = [
            {
                "question": "Who is the main character in 'Attack on Titan'?",
                "options": ["Eren Yeager", "Levi Ackerman", "Mikasa Ackerman", "Armin Arlert"],
                "correct": 0
            },
            {
                "question": "What is the name of Luffy's pirate crew?",
                "options": ["Straw Hat Pirates", "Red Hair Pirates", "Whitebeard Pirates", "Blackbeard Pirates"],
                "correct": 0
            },
            {
                "question": "In 'Naruto', what is the name of the Nine-Tailed Fox?",
                "options": ["Kurama", "Shukaku", "Matatabi", "Isobu"],
                "correct": 0
            }
        ]
        self.active_quizzes: Dict[int, Dict] = {}

class AnimeGroupManager:
    def __init__(self):
        self.warned_users: Dict[int, List[datetime]] = {}
        self.muted_users: Dict[int, datetime] = {}
        self.last_message: Dict[int, datetime] = {}
        self.last_xp_gain: Dict[int, datetime] = {}
        self.user_levels = UserLevel()
        self.anime_quiz = AnimeQuiz()
        self.auto_delete_tasks: List[asyncio.Task] = []
        
    # === NEW FEATURE: Level System ===
    async def handle_level_system(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle XP gain and level system."""
        if not config.LEVEL_CONFIG["ENABLE_LEVEL_SYSTEM"]:
            return
        
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name
        current_time = datetime.now()
        
        # Check cooldown
        if user_id in self.last_xp_gain:
            time_diff = (current_time - self.last_xp_gain[user_id]).total_seconds()
            if time_diff < config.LEVEL_CONFIG["XP_COOLDOWN"]:
                return
        
        # Add XP
        level, xp, leveled_up = self.user_levels.add_xp(
            user_id, username, config.LEVEL_CONFIG["XP_PER_MESSAGE"]
        )
        
        self.last_xp_gain[user_id] = current_time
        
        # Send level up message
        if leveled_up:
            level_up_msg = random.choice(config.LEVEL_CONFIG["LEVEL_UP_MESSAGES"]).format(
                user=update.effective_user.mention_html(),
                level=level
            )
            await update.message.reply_text(level_up_msg, parse_mode='HTML')
    
    async def level_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check user level."""
        user_id = update.effective_user.id
        level, xp = self.user_levels.get_user_level(user_id)
        xp_needed = (level + 1) ** 2 * 100 - xp
        
        level_text = f"""
🎯 *Level Info* 🎯

User: {update.effective_user.mention_html()}
Level: {level} 🏅
XP: {xp} ⭐
XP to next level: {xp_needed}

Keep chatting to level up! 💪
        """
        await update.message.reply_text(level_text, parse_mode='HTML')
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show leaderboard."""
        leaderboard = self.user_levels.get_leaderboard(10)
        
        if not leaderboard:
            await update.message.reply_text("📊 No users on leaderboard yet!")
            return
        
        leaderboard_text = "🏆 *Anime Community Leaderboard* 🏆\n\n"
        for i, (username, level, xp, messages) in enumerate(leaderboard, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            leaderboard_text += f"{medal} @{username} - Level {level} (XP: {xp})\n"
        
        await update.message.reply_text(leaderboard_text, parse_mode='HTML')
    
    # === NEW FEATURE: Anime Character Info ===
    async def character_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get anime character information."""
        if not context.args:
            characters_list = " | ".join([f"`{char}`" for char in config.ANIME_CHARACTERS.keys()])
            await update.message.reply_text(
                f"Available characters: {characters_list}\n"
                f"Usage: `/character naruto`"
            )
            return
        
        character_name = context.args[0].lower()
        character = config.ANIME_CHARACTERS.get(character_name)
        
        if not character:
            await update.message.reply_text("❌ Character not found! Use `/characters` to see available characters.")
            return
        
        character_text = f"""
🎭 *{character['name']}* 🎭

*Series:* {character['series']}
*Quote:* "{character['quote']}"
*Description:* {character['description']}
        """
        
        try:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=character['image'],
                caption=character_text,
                parse_mode='HTML'
            )
        except:
            await update.message.reply_text(character_text, parse_mode='HTML')
    
    # === NEW FEATURE: Anime Polls ===
    async def poll_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create an anime-themed poll."""
        question = random.choice(config.ANIME_POLL_QUESTIONS)
        options = ["Option A", "Option B", "Option C", "Option D"]
        
        poll_message = await context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )
        
        # Store poll data
        payload = {
            poll_message.poll.id: {
                "questions": question,
                "message_id": poll_message.message_id,
                "chat_id": update.effective_chat.id,
                "answers": 0
            }
        }
        context.bot_data.update(payload)
    
    async def receive_poll_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Receive poll answers."""
        answer = update.poll_answer
        poll_id = answer.poll_id
        
        if poll_id not in context.bot_data:
            return
        
        context.bot_data[poll_id]["answers"] += 1
    
    # === NEW FEATURE: Anime Quiz ===
    async def quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start an anime quiz."""
        chat_id = update.effective_chat.id
        
        if chat_id in self.anime_quiz.active_quizzes:
            await update.message.reply_text("❌ There's already an active quiz in this chat!")
            return
        
        question_data = random.choice(self.anime_quiz.questions)
        poll_message = await context.bot.send_poll(
            chat_id=chat_id,
            question=question_data["question"],
            options=question_data["options"],
            type=Poll.QUIZ,
            correct_option_id=question_data["correct"],
            is_anonymous=False
        )
        
        self.anime_quiz.active_quizzes[chat_id] = {
            "poll_id": poll_message.poll.id,
            "question": question_data["question"],
            "correct_option": question_data["correct"]
        }
    
    # === NEW FEATURE: Auto-Delete Messages ===
    async def auto_delete_message(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int):
        """Auto-delete message after delay."""
        await asyncio.sleep(delay)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logger.error(f"Failed to auto-delete message: {e}")
    
    # === NEW FEATURE: Custom Commands ===
    async def waifu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show random waifu info."""
        waifus = [
            {"name": "Rem", "series": "Re:Zero", "image": "https://i.imgur.com/rem_image.jpg"},
            {"name": "Asuna", "series": "Sword Art Online", "image": "https://i.imgur.com/asuna_image.jpg"},
            {"name": "Zero Two", "series": "Darling in the Franxx", "image": "https://i.imgur.com/zerotwo_image.jpg"},
        ]
        
        waifu = random.choice(waifus)
        waifu_text = f"""
💖 *Waifu of the Day* 💖

*Name:* {waifu['name']}
*Series:* {waifu['series']}
*Status:* Best Girl! 💕
        """
        
        try:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=waifu['image'],
                caption=waifu_text,
                parse_mode='HTML'
            )
        except:
            await update.message.reply_text(waifu_text, parse_mode='HTML')
    
    async def animequiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start interactive anime quiz."""
        await self.quiz_command(update, context)
    
    async def recommend_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Recommend random anime."""
        anime_list = [
            {"title": "Attack on Titan", "genre": "Action, Dark Fantasy", "rating": "9.0/10"},
            {"title": "Fullmetal Alchemist: Brotherhood", "genre": "Adventure, Fantasy", "rating": "9.1/10"},
            {"title": "Death Note", "genre": "Thriller, Psychological", "rating": "8.6/10"},
            {"title": "My Hero Academia", "genre": "Action, Superhero", "rating": "8.4/10"},
            {"title": "Demon Slayer", "genre": "Action, Fantasy", "rating": "8.7/10"},
        ]
        
        anime = random.choice(anime_list)
        recommend_text = f"""
🎬 *Anime Recommendation* 🎬

*Title:* {anime['title']}
*Genre:* {anime['genre']}
*Rating:* {anime['rating']}
*Status:* Must Watch! 🌟
        """
        await update.message.reply_text(recommend_text, parse_mode='HTML')
    
    # === NEW FEATURE: Group Statistics ===
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show group statistics."""
        total_users = len(self.user_levels.get_leaderboard(1000))
        active_today = self._get_active_users_count(24)
        
        stats_text = f"""
📈 *Group Statistics* 📈

*Total Members:* {total_users}
*Active Today:* {active_today}
*Total Warnings Issued:* {sum(len(warns) for warns in self.warned_users.values())}
*Level System:* {'✅ Enabled' if config.LEVEL_CONFIG['ENABLE_LEVEL_SYSTEM'] else '❌ Disabled'}

*Bot Uptime:* {self._get_uptime()}
        """
        await update.message.reply_text(stats_text, parse_mode='HTML')
    
    def _get_active_users_count(self, hours: int) -> int:
        """Get count of users active in last N hours."""
        cursor = self.user_levels.conn.cursor()
        time_threshold = datetime.now() - timedelta(hours=hours)
        cursor.execute(
            'SELECT COUNT(*) FROM user_levels WHERE last_message_time > ?',
            (time_threshold,)
        )
        return cursor.fetchone()[0]
    
    def _get_uptime(self) -> str:
        """Get bot uptime."""
        if hasattr(self, 'start_time'):
            uptime = datetime.now() - self.start_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days}d {hours}h {minutes}m {seconds}s"
        return "Unknown"
    
    # === Enhanced Existing Commands ===
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when the command /start is issued."""
        user = update.effective_user
        welcome_text = f"""
🌸 *Anime Guardian Bot* 🌸

Konnichiwa {user.mention_html()}! I'm your anime-themed group management bot!

*New Features Added:*
• 🎯 Level System - Earn XP by chatting
• 🎭 Character Info - Get anime character details
• 📊 Polls & Quizzes - Interactive anime content
• 🏆 Leaderboard - Compete with friends
• 💖 Waifu/Husbando Commands
• 🎬 Anime Recommendations

Use /help to see all commands!
        """
        message = await update.message.reply_text(welcome_text, parse_mode='HTML')
        
        # Auto-delete start message
        if config.AUTO_DELETE["ENABLE_AUTO_DELETE"]:
            asyncio.create_task(self.auto_delete_message(
                context, update.effective_chat.id, message.message_id,
                config.AUTO_DELETE["COMMAND_DELETE_DELAY"]
            ))
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message."""
        help_text = """
🎌 *Anime Guardian Bot - Help* 🎌

*Admin Commands:*
/warn @user - Warn a user
/mute @user - Mute a user
/unmute @user - Unmute a user
/ban @user - Ban a user
/kick @user - Kick a user
/warnings @user - Check warnings

*New Features:*
/level - Check your level
/leaderboard - Show top users
/character <name> - Get character info
/poll - Create anime poll
/quiz - Start anime quiz
/waifu - Random waifu
/recommend - Anime recommendation
/stats - Group statistics

*Basic Commands:*
/start - Welcome message
/help - This message
/quote - Random anime quote
/rules - Group rules
        """
        message = await update.message.reply_text(help_text, parse_mode='HTML')
        
        # Auto-delete help message
        if config.AUTO_DELETE["ENABLE_AUTO_DELETE"]:
            asyncio.create_task(self.auto_delete_message(
                context, update.effective_chat.id, message.message_id,
                config.AUTO_DELETE["COMMAND_DELETE_DELAY"]
            ))
    
    async def welcome_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome new members with anime-themed message and image."""
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                await update.message.reply_text(config.RESPONSES["welcome_bot"])
            else:
                await self._send_welcome_with_image(update, context, member)
    
    async def _send_welcome_with_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE, member):
        """Send welcome message with anime image."""
        welcome_msg = random.choice(config.ANIME_WELCOME_MESSAGES).format(
            user=member.mention_html()
        )
        
        full_welcome_text = f"""
{welcome_msg}

🏮 *New Features* 🏮
• Level System: Chat to earn XP
• Anime Quizzes: Test your knowledge  
• Character Info: Learn about anime characters
• Polls: Vote on anime topics

Use /help to explore all features!
        """
        
        if config.ENABLE_WELCOME_IMAGE:
            try:
                image_url = random.choice(config.WELCOME_IMAGE_URLS)
                
                if config.WELCOME_IMAGE_CAPTION:
                    message = await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=image_url,
                        caption=full_welcome_text,
                        parse_mode='HTML'
                    )
                else:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=image_url
                    )
                    message = await update.message.reply_text(full_welcome_text, parse_mode='HTML')
                
                # Auto-delete welcome message
                if config.AUTO_DELETE["ENABLE_AUTO_DELETE"]:
                    asyncio.create_task(self.auto_delete_message(
                        context, update.effective_chat.id, message.message_id,
                        config.AUTO_DELETE["WELCOME_DELETE_DELAY"]
                    ))
                    
            except Exception as e:
                logger.error(f"Failed to send welcome image: {e}")
                message = await update.message.reply_text(
                    f"{config.RESPONSES['image_send_failed']}\n\n{full_welcome_text}",
                    parse_mode='HTML'
                )
        else:
            message = await update.message.reply_text(full_welcome_text, parse_mode='HTML')
    
    # ... (Keep all the existing moderation commands: warn, mute, ban, etc.)

    async def run_cleanup_tasks(self):
        """Run periodic cleanup tasks."""
        while True:
            self.cleanup_old_data()
            await asyncio.sleep(3600)  # Run every hour

def main():
    """Start the bot."""
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    manager = AnimeGroupManager()
    manager.start_time = datetime.now()
    
    # Add handlers
    application.add_handler(CommandHandler("start", manager.start))
    application.add_handler(CommandHandler("help", manager.help_command))
    application.add_handler(CommandHandler("quote", manager.send_quote))
    application.add_handler(CommandHandler("rules", manager.show_rules))
    
    # New feature handlers
    application.add_handler(CommandHandler("level", manager.level_command))
    application.add_handler(CommandHandler("leaderboard", manager.leaderboard_command))
    application.add_handler(CommandHandler("character", manager.character_command))
    application.add_handler(CommandHandler("poll", manager.poll_command))
    application.add_handler(CommandHandler("quiz", manager.quiz_command))
    application.add_handler(CommandHandler("waifu", manager.waifu_command))
    application.add_handler(CommandHandler("animequiz", manager.animequiz_command))
    application.add_handler(CommandHandler("recommend", manager.recommend_command))
    application.add_handler(CommandHandler("stats", manager.stats_command))
    
    # Existing moderation handlers
    application.add_handler(CommandHandler("warn", manager.warn_user))
    application.add_handler(CommandHandler("mute", manager.mute_user))
    application.add_handler(CommandHandler("unmute", manager.unmute_user))
    application.add_handler(CommandHandler("ban", manager.ban_user))
    application.add_handler(CommandHandler("kick", manager.kick_user))
    application.add_handler(CommandHandler("warnings", manager.check_warnings))
    
    # Message handlers
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, 
        manager.welcome_new_member
    ))
    
    # Level system handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        manager.handle_level_system
    ))
    
    # Poll handler
    application.add_handler(PollHandler(manager.receive_poll_answer))
    
    # Start cleanup tasks
    asyncio.get_event_loop().create_task(manager.run_cleanup_tasks())
    
    logger.info("🌸 Anime Guardian Bot with New Features is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
