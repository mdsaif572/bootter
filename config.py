from os import getenv

from dotenv import load_dotenv

load_dotenv()


API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")

TOKEN = getenv("TOKEN")
MONGO_DB_URL = getenv("MONGO_DB_URL", None)

OWNER_ID = int(getenv("OWNER_ID", 5938660179))
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/FallenAssociation")

LOGGER_ID = getenv("LOGGER_ID", "-1001819078701")
DEV_USERS = set(int(x) for x in getenv("DEV_USERS", "").split())
