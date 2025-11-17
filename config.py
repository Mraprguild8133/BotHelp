import os
from typing import List, Dict

class Config:
    """Configuration class for Anime Guardian Bot"""
    
    # Bot Token from BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Admin user IDs (get from @userinfobot)
    ADMIN_IDS: List[int] = [6300568870]  # Replace with actual user IDs
    
    # Database settings
    DATABASE_NAME = "anime_bot.db"
    
    # Group settings
    MAX_WARNINGS = 3
    MUTE_DURATION_HOURS = 1
    WARNING_EXPIRE_HOURS = 24
    ANTI_SPAM_COOLDOWN = 2  # seconds
    
    # Welcome message settings
    WELCOME_IMAGE_URLS = [
        "https://i.ibb.co/7tw8p570/image.jpg",
        "https://i.ibb.co/FqWwcPt4/image.jpg",
        "https://i.ibb.co/S76ph51d/image.jpg",
    ]
    ENABLE_WELCOME_IMAGE = True
    WELCOME_IMAGE_CAPTION = True
    
    # Anime-themed messages
    ANIME_QUOTES = [
        "Believe in the me that believes in you! - Kamina (Gurren Lagann)",
        "People's dreams never end! - Marshall D. Teach (One Piece)",
        "If you don't like your destiny, don't accept it. - Naruto Uzumaki",
        "Hard work is worthless for those that don't believe in themselves. - Naruto Uzumaki",
        "It's not the face that makes someone a monster, it's the choices they make. - Naruto Uzumaki",
        "I am the hope of the universe. - Son Goku (Dragon Ball Z)",
        "It's not the world that's imperfect. It's we who are imperfect. - Lelouch vi Britannia",
        "The world isn't perfect. But it's there for us, doing the best it can. - Roy Mustang",
        "A lesson without pain is meaningless. - Edward Elric (Fullmetal Alchemist)",
        "The world is not beautiful, therefore it is. - Kino (Kino's Journey)"
    ]
    
    ANIME_WELCOME_MESSAGES = [
        "Welcome {user}! You've entered the world of anime! 🌸",
        "Konichiwa {user}! Ready for some anime adventures? ✨",
        "Welcome {user}! May your stay be as exciting as a shonen battle! ⚔️",
        "Yōkoso {user}! The anime realm welcomes you! 🎌",
        "Welcome {user}! Let the anime journey begin! 🎮",
        "Irasshaimase {user}! The anime dojo welcomes you! 🥋",
        "Welcome {user}! Your anime adventure starts now! 🌟",
        "Welcome {user}! Grab some ramen and enjoy the anime vibes! 🍜"
    ]
    
    # Anime Character Database
    ANIME_CHARACTERS = {
        "naruto": {
            "name": "Naruto Uzumaki",
            "series": "Naruto",
            "image": "https://i.ibb.co/d0LTPTyq/image.jpg",
            "quote": "I'm not gonna run away, I never go back on my word!",
            "description": "A shinobi of Konohagakure's Uzumaki clan who dreams of becoming Hokage."
        },
        "goku": {
            "name": "Son Goku",
            "series": "Dragon Ball",
            "image": "https://i.ibb.co/nqQwK6gg/image.jpg",
            "quote": "I am the hope of the universe.",
            "description": "Saiyan raised on Earth and the main protagonist of Dragon Ball series."
        },
        "luffy": {
            "name": "Monkey D. Luffy",
            "series": "One Piece",
            "image": "https://i.ibb.co/4RCwZnVn/image.jpg",
            "quote": "I'm gonna be King of the Pirates!",
            "description": "Captain of the Straw Hat Pirates with rubber powers from the Gum-Gum Fruit."
        },
        "saitama": {
            "name": "Saitama",
            "series": "One Punch Man",
            "image": "https://i.ibb.co/vxzsg5bT/image.jpg",
            "quote": "I'm just a hero for fun.",
            "description": "A hero who can defeat any opponent with a single punch."
        },
        "levi": {
            "name": "Levi Ackerman",
            "series": "Attack on Titan",
            "image": "https://i.ibb.co/W4wzpL73/image.jpg",
            "quote": "Give up on your dreams and die.",
            "description": "Captain of the Survey Corps and humanity's strongest soldier."
        },
        "eren": {
            "name": "Eren Yeager",
            "series": "Attack on Titan",
            "image": "https://i.ibb.co/ynGnjK7d/image.jpg",
            "quote": "I'm going to destroy every last one of them!",
            "description": "The main protagonist who possesses the power of the Attack Titan."
        },
        "gojo": {
            "name": "Satoru Gojo",
            "series": "Jujutsu Kaisen",
            "image": "https://i.ibb.co/bj1NZ0FP/image.jpg",
            "quote": "Throughout Heaven and Earth, I alone am the honored one.",
            "description": "The strongest jujutsu sorcerer and teacher at Tokyo Jujutsu High."
        },
        "nezuko": {
            "name": "Nezuko Kamado",
            "series": "Demon Slayer",
            "image": "https://i.ibb.co/7xwTRQKq/image.jpg",
            "quote": "*Muffled sounds*",
            "description": "Tanjiro's younger sister who was turned into a demon but retains her humanity."
        },
        "light": {
            "name": "Light Yagami",
            "series": "Death Note",
            "image": "https://i.ibb.co/QvkF7vpC/image.jpg",
            "quote": "I am justice!",
            "description": "A genius high school student who obtains the Death Note and becomes Kira."
        },
        "asuna": {
            "name": "Asuna Yuuki",
            "series": "Sword Art Online",
            "image": "https://i.ibb.co/pvHxR3hs/image.jpg",
            "quote": "I'm not going to run away anymore...",
            "description": "The Sub-Commander of the Knights of the Blood and Kirito's love interest."
        }
    }
    
    # Level System Configuration
    LEVEL_CONFIG = {
        "ENABLE_LEVEL_SYSTEM": True,
        "XP_PER_MESSAGE": 5,
        "XP_COOLDOWN": 60,  # seconds between XP gains
        "LEVEL_UP_MESSAGES": [
            "🎉 {user} leveled up to level {level}! Sugoi!",
            "🌟 {user} reached level {level}! Amazing growth!",
            "🏆 Level up! {user} is now level {level}!",
            "✨ {user} leveled up! Now at level {level}! Keep going!",
            "🎯 Level up achieved! {user} is now level {level}!",
        ]
    }
    
    # Auto-Delete Settings
    AUTO_DELETE = {
        "ENABLE_AUTO_DELETE": True,
        "COMMAND_DELETE_DELAY": 30,  # seconds
        "WELCOME_DELETE_DELAY": 300,  # seconds
        "RULES_DELETE_DELAY": 600,  # seconds
    }
    
    # Custom Commands Description
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
        "image_send_failed": "Failed to send welcome image, sending text welcome instead.",
        "database_error": "❌ Database error occurred. Please try again later."
    }
    
    # Rules
    GROUP_RULES = """
📜 *Anime Community Rules* 📜

1. 🤝 *Be Respectful* - Treat everyone with respect and kindness
2. 🎭 *Stay On Topic* - Keep discussions anime and manga related
3. 🚫 *No Spam* - Don't flood the chat with messages
4. 📛 *No NSFW Content* - Keep everything safe for work
5. 🔗 *No Unsolicited Links* - Ask before posting external links
6. 👥 *No Harassment* - Bullying and harassment won't be tolerated
7. 🎨 *Credit Artists* - Always credit fan art and content creators
8. 🏷️ *Use Appropriate Language* - Keep conversations friendly and appropriate
9. 📢 *No Advertising* - Don't advertise without permission
10. 🤖 *Respect the Bot* - Don't spam bot commands

*Consequences for violations:*
• 1st offense: Warning
• 2nd offense: 1-hour mute
• 3rd offense: 24-hour mute
• 4th offense: Permanent ban

Let's keep this community awesome for everyone! ✨
    """
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Feature toggles
    FEATURES = {
        "WELCOME_MESSAGES": True,
        "LEVEL_SYSTEM": True,
        "ANTI_SPAM": True,
        "AUTO_DELETE": False,  # Set to True if you want auto-delete
        "CHARACTER_DATABASE": True,
        "QUIZ_SYSTEM": True,
    }
    
    # Anime recommendations (FIXED - removed + from numbers)
    ANIME_RECOMMENDATIONS = [
        {
            "title": "Attack on Titan",
            "genre": "Action, Dark Fantasy, Drama",
            "episodes": 75,
            "rating": "9.0/10",
            "description": "Humans fight for survival against giant humanoid creatures called Titans."
        },
        {
            "title": "Fullmetal Alchemist: Brotherhood",
            "genre": "Adventure, Fantasy, Steampunk",
            "episodes": 64,
            "rating": "9.1/10",
            "description": "Two brothers search for the Philosopher's Stone to restore their bodies."
        },
        {
            "title": "Death Note",
            "genre": "Thriller, Psychological, Supernatural",
            "episodes": 37,
            "rating": "8.6/10",
            "description": "A high school student discovers a notebook that can kill anyone whose name is written in it."
        },
        {
            "title": "My Hero Academia",
            "genre": "Action, Superhero, School",
            "episodes": 113,
            "rating": "8.4/10",
            "description": "A boy born without superpowers in a superhuman society dreams of becoming a hero."
        },
        {
            "title": "Demon Slayer",
            "genre": "Action, Fantasy, Supernatural",
            "episodes": 55,
            "rating": "8.7/10",
            "description": "A young boy becomes a demon slayer to save his sister and avenge his family."
        },
        {
            "title": "One Punch Man",
            "genre": "Action, Comedy, Superhero",
            "episodes": 24,
            "rating": "8.7/10",
            "description": "A hero who can defeat any opponent with a single punch grows bored from a lack of challenge."
        },
        {
            "title": "Jujutsu Kaisen",
            "genre": "Action, Supernatural, Horror",
            "episodes": 24,
            "rating": "8.6/10",
            "description": "A boy eats a cursed finger and becomes the vessel for a powerful curse."
        },
        {
            "title": "Hunter x Hunter",
            "genre": "Adventure, Fantasy, Martial Arts",
            "episodes": 148,
            "rating": "9.0/10",
            "description": "A young boy aspires to become a Hunter to find his missing father."
        },
        {
            "title": "Steins;Gate",
            "genre": "Sci-Fi, Thriller, Romance",
            "episodes": 24,
            "rating": "9.1/10",
            "description": "A group of friends discover time travel and face its dangerous consequences."
        },
        {
            "title": "Cowboy Bebop",
            "genre": "Action, Sci-Fi, Noir",
            "episodes": 26,
            "rating": "8.9/10",
            "description": "Bounty hunters travel through space in their ship, the Bebop."
        }
    ]
    
    # Waifu database (for fun commands)
    WAIFUS = [
        {
            "name": "Rem",
            "series": "Re:Zero",
            "image": "https://i.imgur.com/rem_image.jpg",
            "description": "A demon maid who is fiercely loyal and protective.",
            "personality": "Loyal, Protective, Caring"
        },
        {
            "name": "Zero Two",
            "series": "Darling in the Franxx",
            "image": "https://i.imgur.com/zerotwo_image.jpg",
            "description": "A mysterious girl with red horns and exceptional piloting skills.",
            "personality": "Confident, Mysterious, Passionate"
        },
        {
            "name": "Mikasa Ackerman",
            "series": "Attack on Titan",
            "image": "https://i.imgur.com/mikasa_image.jpg",
            "description": "One of the last remaining Asians and a skilled soldier.",
            "personality": "Loyal, Strong, Protective"
        },
        {
            "name": "Asuna Yuuki",
            "series": "Sword Art Online",
            "image": "https://i.imgur.com/asuna_image.jpg",
            "description": "The Sub-Commander of the Knights of the Blood.",
            "personality": "Kind, Strong, Determined"
        },
        {
            "name": "Nezuko Kamado",
            "series": "Demon Slayer",
            "image": "https://i.imgur.com/nezuko_image.jpg",
            "description": "Tanjiro's younger sister turned into a demon.",
            "personality": "Gentle, Protective, Caring"
        }
    ]
    
    # Husbando database (for fun commands)
    HUSBANDOS = [
        {
            "name": "Levi Ackerman",
            "series": "Attack on Titan",
            "image": "https://i.imgur.com/levi_image.jpg",
            "description": "Captain of the Survey Corps and humanity's strongest soldier.",
            "personality": "Clean, Strong, Serious"
        },
        {
            "name": "Satoru Gojo",
            "series": "Jujutsu Kaisen",
            "image": "https://i.imgur.com/gojo_image.jpg",
            "description": "The strongest jujutsu sorcerer with incredible powers.",
            "personality": "Confident, Playful, Powerful"
        },
        {
            "name": "Kakashi Hatake",
            "series": "Naruto",
            "image": "https://i.imgur.com/kakashi_image.jpg",
            "description": "The Copy Ninja with a mysterious past and powerful abilities.",
            "personality": "Calm, Intelligent, Mysterious"
        },
        {
            "name": "Lelouch vi Britannia",
            "series": "Code Geass",
            "image": "https://i.imgur.com/lelouch_image.jpg",
            "description": "A prince who gains the power of Geass and leads a rebellion.",
            "personality": "Intelligent, Strategic, Charismatic"
        },
        {
            "name": "Spike Spiegel",
            "series": "Cowboy Bebop",
            "image": "https://i.imgur.com/spike_image.jpg",
            "description": "A bounty hunter with a mysterious past and martial arts skills.",
            "personality": "Cool, Laid-back, Skilled"
        }
    ]

# Create config instance
config = Config()
