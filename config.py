import logging
from logging.handlers import RotatingFileHandler

# Bot Configuration
LOG_FILE_NAME = "bot.log"
PORT = '4410'                         # ← OLD VALUE
OWNER_ID = 1327021082                 # ← OLD VALUE

MSG_EFFECT = 5046509860389126442      # ← OLD VALUE

# NEW variable names – OLD values inserted
SHORT_URL_1 = "arolinks.com"          # OLD SHORT_URL
SHORT_API_1 = "2b3dd0b54ab06c6c8e6cf617f20d5fff15ee1b71"

SHORT_URL_2 = "arolinks.com"          # same as old (you had only 1)
SHORT_API_2 = "2b3dd0b54ab06c6c8e6cf617f20d5fff15ee1b71"

SHORT_TUT = "https://t.me/How_to_Download_7x/26"

# Bot Login
SESSION = "yato"
TOKEN = "5717147729:AAHf-p-YAP5Oyor4xKToTZKlr9TC6Wt1JOY"
API_ID = "27353035"
API_HASH = "cf2a75861140ceb746c7796e07cbde9e"
WORKERS = 5

# Database
DB_URI = "mongodb+srv://poulomig644_db_user:d9MMUd5PsTP5MDFf@cluster0.q5evcku.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "yato"

FSUBS = [[-1001918476761, True, 10]]      # OLD VALUE

DB_CHANNEL = -1001918476761               # OLD VALUE

AUTO_DEL = 300                            # OLD VALUE

ADMINS = [1327021082, 1327021082]         # OLD VALUE

DISABLE_BTN = True
PROTECT = True

# Messages
MESSAGES = { ... (same as old config) ... }

def LOGGER(name: str, client_name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        f"[%(asctime)s - %(levelname)s] - {client_name} - %(name)s - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S'
    )
    file_handler = RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
