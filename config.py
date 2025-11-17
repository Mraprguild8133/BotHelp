import os
from typing import List, Dict

class Config:
    """Configuration class for Anime Guardian Bot"""
    
    # Bot Token from BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Admin user IDs (get from @userinfobot)
    ADMIN_IDS: List[int] = [6300568870]  # Replace with actual user IDs
    
    # Group settings
    MAX_WARNINGS = 3
    MUTE_DURATION_HOURS = 1
    WARNING_EXPIRE_HOURS = 24
    ANTI_SPAM_COOLDOWN = 2  # seconds
    
    # Welcome message settings
    WELCOME_IMAGE_URLS = [
        "https://i.imgur.com/8SqjK2v.png",
        "https://i.imgur.com/9X8qjK2.png",
        "https://i.imgur.com/7WqjK2v.png",
    ]
    ENABLE_WELCOME_IMAGE = True
    WELCOME_IMAGE_CAPTION = True
    
    # Anime-themed messages
    ANIME_QUOTES = [
        "Believe in the me that believes in you! - Kamina (Gurren Lagann)",
        "People's dreams never end! - Marshall D. Teach (One Piece)",
        "If you don't like your destiny, don't accept it. - Naruto Uzumaki",
        "Hard work is worthless for those that don't believe in themselves. - Naruto Uzumaki",
    ]
    
    ANIME_WELCOME_MESSAGES = [
        "Welcome {user}! You've entered the world of anime! 🌸",
        "Konichiwa {user}! Ready for some anime adventures? ✨",
        "Welcome {user}! May your stay be as exciting as a shonen battle! ⚔️",
    ]
    
    # New Feature: Anime Character Database
    ANIME_CHARACTERS = {
        "naruto": {
            "name": "Naruto Uzumaki",
            "series": "Naruto",
            "image": "https://i.imgur.com/naruto_image.jpg",
            "quote": "I'm not gonna run away, I never go back on my word!",
            "description": "A shinobi of Konohagakure's Uzumaki clan."
        },
        "goku": {
            "name": "Son Goku",
            "series": "Dragon Ball",
            "image": "https://i.imgur.com/goku_image.jpg",
            "quote": "I am the hope of the universe.",
            "description": "Saiyan raised on Earth and the main protagonist."
        },
        "luffy": {
            "name": "Monkey D. Luffy",
            "series": "One Piece",
            "image": "https://i.imgur.com/luffy_image.jpg",
            "quote": "I'm gonna be King of the Pirates!",
            "description": "Captain of the Straw Hat Pirates."
        }
    }
    
    # New Feature: Anime Poll Questions
    ANIME_POLL_QUESTIONS = [
        "Which anime has the best character development?",
        "Who is the strongest anime character?",
        "Best anime soundtrack?",
        "Most emotional anime scene?",
        "Favorite anime genre?",
        "Best anime villain?"
    ]
    
    # New Feature: Level System
    LEVEL_CONFIG = {
        "ENABLE_LEVEL_SYSTEM": True,
        "XP_PER_MESSAGE": 5,
        "XP_COOLDOWN": 60,  # seconds
        "LEVEL_UP_MESSAGES": [
            "🎉 {user} leveled up to level {level}! Sugoi!",
            "🌟 {user} reached level {level}! Amazing growth!",
            "🏆 Level up! {user} is now level {level}!",
        ]
    }
    
    # New Feature: Auto-Delete Settings
    AUTO_DELETE = {
        "ENABLE_AUTO_DELETE": True,
        "COMMAND_DELETE_DELAY": 30,  # seconds
        "WELCOME_DELETE_DELAY": 300,  # seconds
        "RULES_DELETE_DELAY": 600,  # seconds
    }
    
    # New Feature: Custom Commands
    CUSTOM_COMMANDS = {
        "waifu": "Shows random waifu image and info",
        "husbando": "Shows random husbando image and info",
        "animequiz": "Starts an anime quiz",
        "recommend": "Recommends random anime",
        "schedule": "Shows anime airing schedule"
    }
    
    # Bot responses
    RESPONSES = {
        "no_permission": "❌ You need to be an admin to use this command!",
        "no_user_mentioned": "❌ Please mention a user!\nUsage: {usage}",
        "user_not_found": "❌ Could not find the mentioned user!",
        "command_failed": "❌ Failed to execute command: {error}",
        "welcome_bot": "Arigatou for adding me! I'll protect this anime community! 🌸\nUse /help to see my commands!",
        "spam_warning": "{user} please don't spam! 🚫",
        "image_send_failed": "Failed to send image, sending text instead."
    }
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Create config instance
config = Config()
