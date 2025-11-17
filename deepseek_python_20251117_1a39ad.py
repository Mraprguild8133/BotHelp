import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from telegram import Update, ChatMember, ChatPermissions
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackContext, ChatMemberHandler
)

# Bot Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_IDS = []  # Add admin user IDs here
ANIME_QUOTES = [
    "Believe in the me that believes in you! - Kamina (Gurren Lagann)",
    "People's dreams never end! - Marshall D. Teach (One Piece)",
    "If you don't like your destiny, don't accept it. - Naruto Uzumaki",
    "Hard work is worthless for those that don't believe in themselves. - Naruto Uzumaki",
    "It's not the face that makes someone a monster, it's the choices they make. - Naruto Uzumaki"
]

ANIME_WELCOME_MESSAGES = [
    "Welcome {user}! You've entered the world of anime! 🌸",
    "Konichiwa {user}! Ready for some anime adventures? ✨",
    "Welcome {user}! May your stay be as exciting as a shonen battle! ⚔️",
    "Yōkoso {user}! The anime realm welcomes you! 🎌",
    "Welcome {user}! Let the anime journey begin! 🎮"
]

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AnimeGroupManager:
    def __init__(self):
        self.warned_users: Dict[int, List[datetime]] = {}
        self.muted_users: Dict[int, datetime] = {}
        self.last_message: Dict[int, datetime] = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when the command /start is issued."""
        user = update.effective_user
        welcome_text = f"""
🌸 *Anime Guardian Bot* 🌸

Konnichiwa {user.mention_html()}! I'm your anime-themed group management bot!

*Available Commands:*
• /start - Show this welcome message
• /help - Show help information
• /quote - Get a random anime quote
• /rules - Show group rules
• /warn @user - Warn a user
• /mute @user - Mute a user
• /unmute @user - Unmute a user
• /ban @user - Ban a user
• /kick @user - Kick a user
• /warnings @user - Check user warnings

Let's keep this community awesome! ✨
        """
        await update.message.reply_text(welcome_text, parse_mode='HTML')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message."""
        help_text = """
🎌 *Anime Guardian Bot - Help* 🎌

*Admin Commands:*
/warn @user - Warn a user (3 warnings = auto-ban)
/mute @user - Mute a user for 1 hour
/unmute @user - Unmute a user
/ban @user - Ban a user from the group
/kick @user - Kick a user from the group
/warnings @user - Check user warnings

*User Commands:*
/start - Welcome message
/help - This help message
/quote - Random anime quote
/rules - Group rules

*Features:*
• Auto-welcome new members
• Anti-spam protection
• Warning system
• Anime-themed responses
        """
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def send_quote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a random anime quote."""
        quote = random.choice(ANIME_QUOTES)
        await update.message.reply_text(f"💫 *Anime Quote of the Moment:*\n\n{quote}", parse_mode='HTML')
    
    async def show_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show group rules."""
        rules_text = """
📜 *Anime Community Rules* 📜

1. 🤝 *Be Respectful* - Treat everyone with respect
2. 🎭 *Stay On Topic* - Keep discussions anime-related
3. 🚫 *No Spam* - Don't flood the chat
4. 📛 *No NSFW* - Keep content safe for work
5. 🔗 *No Unsolicited Links* - Ask before posting links
6. 👥 *No Harassment* - Bullying won't be tolerated
7. 🎨 *Credit Artists* - Always credit fan art creators

*Violations may result in warnings, mutes, or bans.*
        """
        await update.message.reply_text(rules_text, parse_mode='HTML')
    
    async def welcome_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome new members with anime-themed message."""
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                # Bot was added to group
                await update.message.reply_text(
                    "Arigatou for adding me! I'll protect this anime community! 🌸\n"
                    "Use /help to see my commands!"
                )
            else:
                welcome_msg = random.choice(ANIME_WELCOME_MESSAGES).format(
                    user=member.mention_html()
                )
                await update.message.reply_text(welcome_msg, parse_mode='HTML')
    
    async def warn_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Warn a user."""
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please mention a user to warn!\nUsage: /warn @username")
            return
        
        target_user = await self._get_mentioned_user(update, context)
        if not target_user:
            await update.message.reply_text("❌ Could not find the mentioned user!")
            return
        
        user_id = target_user.id
        current_time = datetime.now()
        
        # Initialize warnings list for user
        if user_id not in self.warned_users:
            self.warned_users[user_id] = []
        
        # Add warning
        self.warned_users[user_id].append(current_time)
        warning_count = len(self.warned_users[user_id])
        
        warning_text = f"""
⚠️ *Warning Issued* ⚠️

User: {target_user.mention_html()}
Warnings: {warning_count}/3
Issued by: {update.effective_user.mention_html()}

*Next step:* {f"Ban at 3 warnings" if warning_count < 3 else "BAN IMMINENT!"}
        """
        
        await update.message.reply_text(warning_text, parse_mode='HTML')
        
        # Auto-ban at 3 warnings
        if warning_count >= 3:
            await self.ban_user_manual(update, context, target_user, "Automatically banned for reaching 3 warnings")
            # Clear warnings after ban
            if user_id in self.warned_users:
                del self.warned_users[user_id]
    
    async def mute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mute a user for 1 hour."""
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please mention a user to mute!\nUsage: /mute @username")
            return
        
        target_user = await self._get_mentioned_user(update, context)
        if not target_user:
            await update.message.reply_text("❌ Could not find the mentioned user!")
            return
        
        user_id = target_user.id
        mute_duration = timedelta(hours=1)
        unmute_time = datetime.now() + mute_duration
        
        # Set permissions to restrict sending messages
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )
        
        try:
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id,
                permissions=permissions,
                until_date=unmute_time
            )
            
            self.muted_users[user_id] = unmute_time
            
            mute_text = f"""
🔇 *User Muted* 🔇

User: {target_user.mention_html()}
Duration: 1 hour
Muted by: {update.effective_user.mention_html()}
Unmute at: {unmute_time.strftime('%Y-%m-%d %H:%M:%S')}
            """
            await update.message.reply_text(mute_text, parse_mode='HTML')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to mute user: {str(e)}")
    
    async def unmute_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unmute a user."""
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please mention a user to unmute!\nUsage: /unmute @username")
            return
        
        target_user = await self._get_mentioned_user(update, context)
        if not target_user:
            await update.message.reply_text("❌ Could not find the mentioned user!")
            return
        
        user_id = target_user.id
        
        # Restore normal permissions
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        
        try:
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=user_id,
                permissions=permissions
            )
            
            if user_id in self.muted_users:
                del self.muted_users[user_id]
            
            await update.message.reply_text(
                f"🔊 {target_user.mention_html()} has been unmuted! Welcome back! 🎉",
                parse_mode='HTML'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to unmute user: {str(e)}")
    
    async def ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ban a user from the group."""
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please mention a user to ban!\nUsage: /ban @username")
            return
        
        target_user = await self._get_mentioned_user(update, context)
        if not target_user:
            await update.message.reply_text("❌ Could not find the mentioned user!")
            return
        
        await self.ban_user_manual(update, context, target_user, "Banned by admin")
    
    async def ban_user_manual(self, update: Update, context: ContextTypes.DEFAULT_TYPE, target_user, reason):
        """Manual ban function with reason."""
        try:
            await context.bot.ban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=target_user.id
            )
            
            ban_text = f"""
🚫 *User Banned* 🚫

User: {target_user.mention_html()}
Reason: {reason}
Banned by: {update.effective_user.mention_html()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            await update.message.reply_text(ban_text, parse_mode='HTML')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to ban user: {str(e)}")
    
    async def kick_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kick a user from the group."""
        if not await self._is_admin(update, context):
            await update.message.reply_text("❌ You need to be an admin to use this command!")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please mention a user to kick!\nUsage: /kick @username")
            return
        
        target_user = await self._get_mentioned_user(update, context)
        if not target_user:
            await update.message.reply_text("❌ Could not find the mentioned user!")
            return
        
        try:
            await context.bot.ban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=target_user.id,
                until_date=datetime.now() + timedelta(seconds=30)  # Unban after 30 seconds
            )
            
            await update.message.reply_text(
                f"👢 {target_user.mention_html()} has been kicked from the group!",
                parse_mode='HTML'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to kick user: {str(e)}")
    
    async def check_warnings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check warnings for a user."""
        if not context.args:
            await update.message.reply_text("❌ Please mention a user!\nUsage: /warnings @username")
            return
        
        target_user = await self._get_mentioned_user(update, context)
        if not target_user:
            await update.message.reply_text("❌ Could not find the mentioned user!")
            return
        
        user_id = target_user.id
        warning_count = len(self.warned_users.get(user_id, []))
        
        warnings_text = f"""
📊 *Warning Status* 📊

User: {target_user.mention_html()}
Total Warnings: {warning_count}
Status: {"⚠️ Close to ban!" if warning_count >= 2 else "✅ Good standing"}
        """
        await update.message.reply_text(warnings_text, parse_mode='HTML')
    
    async def anti_spam(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Anti-spam protection."""
        user_id = update.effective_user.id
        current_time = datetime.now()
        
        # Check if user is sending messages too quickly
        if user_id in self.last_message:
            time_diff = (current_time - self.last_message[user_id]).total_seconds()
            if time_diff < 2:  # Less than 2 seconds between messages
                # Warn user about spam
                await update.message.reply_text(
                    f"{update.effective_user.mention_html()} please don't spam! 🚫",
                    parse_mode='HTML'
                )
                return
        
        self.last_message[user_id] = current_time
    
    async def _is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if the user is an admin."""
        user_id = update.effective_user.id
        
        # Check if user is in admin list
        if user_id in ADMIN_IDS:
            return True
        
        # Check if user is admin in the group
        try:
            chat_member = await context.bot.get_chat_member(
                update.effective_chat.id,
                user_id
            )
            return chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
        except:
            return False
    
    async def _get_mentioned_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Extract mentioned user from command."""
        try:
            if update.message.reply_to_message:
                return update.message.reply_to_message.from_user
            
            if context.args:
                username = context.args[0].lstrip('@')
                # This is a simplified version - in production, you'd want to implement
                # proper user resolution through Telegram's API
                return type('User', (), {'id': 0, 'mention_html': lambda: username})()
        
        except Exception as e:
            logger.error(f"Error getting mentioned user: {e}")
        
        return None
    
    def cleanup_old_data(self):
        """Clean up old warnings and mutes."""
        current_time = datetime.now()
        
        # Clean old warnings (older than 24 hours)
        for user_id in list(self.warned_users.keys()):
            self.warned_users[user_id] = [
                warn_time for warn_time in self.warned_users[user_id]
                if (current_time - warn_time) < timedelta(hours=24)
            ]
            if not self.warned_users[user_id]:
                del self.warned_users[user_id]
        
        # Clean expired mutes
        for user_id in list(self.muted_users.keys()):
            if current_time > self.muted_users[user_id]:
                del self.muted_users[user_id]

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    manager = AnimeGroupManager()
    
    # Add handlers
    application.add_handler(CommandHandler("start", manager.start))
    application.add_handler(CommandHandler("help", manager.help_command))
    application.add_handler(CommandHandler("quote", manager.send_quote))
    application.add_handler(CommandHandler("rules", manager.show_rules))
    application.add_handler(CommandHandler("warn", manager.warn_user))
    application.add_handler(CommandHandler("mute", manager.mute_user))
    application.add_handler(CommandHandler("unmute", manager.unmute_user))
    application.add_handler(CommandHandler("ban", manager.ban_user))
    application.add_handler(CommandHandler("kick", manager.kick_user))
    application.add_handler(CommandHandler("warnings", manager.check_warnings))
    
    # Welcome new members
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, 
        manager.welcome_new_member
    ))
    
    # Anti-spam for all messages
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        manager.anti_spam
    ))
    
    # Start the Bot
    print("🌸 Anime Guardian Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()