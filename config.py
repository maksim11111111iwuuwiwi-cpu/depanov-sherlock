
import os

# DEPANOV SHERLOCK CONFIG

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

BOT_NAME = "DEPANOV SHERLOCK"
VERSION = "1.0.0"

# Database
DATABASE_NAME = "sherlock.db"

# Logging
LOG_LEVEL = "INFO"

# Search settings
SUPPORTED_PLATFORMS = {
    "Telegram": "https://t.me/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "TikTok": "https://www.tiktok.com/@{}",
    "X": "https://x.com/{}",
    "GitHub": "https://github.com/{}"
}
