import os
from typing import List

class Config:
    """Configuration class for Anime Guardian Bot"""
    
    # Bot Token from BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    # Admin user IDs (get from @userinfobot)
    ADMIN_IDS: List[int] = [6300568870]  # Replace with actual user IDs
    
    # Group settings
    MAX_WARNINGS = 3
    MUTE_DURATION_HOURS = 1
    WARNING_EXPIRE_HOURS = 24
    ANTI_SPAM_COOLDOWN = 2  # seconds
    
    # Anime-themed messages
    ANIME_QUOTES = [
        "Believe in the me that believes in you! - Kamina (Gurren Lagann)",
        "People's dreams never end! - Marshall D. Teach (One Piece)",
        "If you don't like your destiny, don't accept it. - Naruto Uzumaki",
        "Hard work is worthless for those that don't believe in themselves. - Naruto Uzumaki",
        "It's not the face that makes someone a monster, it's the choices they make. - Naruto Uzumaki",
        "I am the hope of the universe. - Son Goku (Dragon Ball Z)",
        "It's not the world that's imperfect. It's we who are imperfect. - Lelouch vi Britannia",
        "The world isn't perfect. But it's there for us, doing the best it can. - Roy Mustang"
    ]
    
    ANIME_WELCOME_MESSAGES = [
        "Welcome {user}! You've entered the world of anime! 🌸",
        "Konichiwa {user}! Ready for some anime adventures? ✨",
        "Welcome {user}! May your stay be as exciting as a shonen battle! ⚔️",
        "Yōkoso {user}! The anime realm welcomes you! 🎌",
        "Welcome {user}! Let the anime journey begin! 🎮",
        "Irasshaimase {user}! The anime dojo welcomes you! 🥋",
        "Welcome {user}! Your anime adventure starts now! 🌟"
    ]
    
    # Bot responses
    RESPONSES = {
        "no_permission": "❌ You need to be an admin to use this command!",
        "no_user_mentioned": "❌ Please mention a user!\nUsage: {usage}",
        "user_not_found": "❌ Could not find the mentioned user!",
        "command_failed": "❌ Failed to execute command: {error}",
        "welcome_bot": "Arigatou for adding me! I'll protect this anime community! 🌸\nUse /help to see my commands!",
        "spam_warning": "{user} please don't spam! 🚫"
    }
    
    # Rules
    GROUP_RULES = """
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
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Create config instance
config = Config()
