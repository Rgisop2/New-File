import logging
from logging.handlers import RotatingFileHandler

# Bot Configuration
LOG_FILE_NAME = "bot.log"
PORT = '4410'
OWNER_ID = 1327021082

MSG_EFFECT = 5046509860389126442

# NEW VARIABLES — OLD VALUES
SHORT_URL_1 = "arolinks.com"
SHORT_API_1 = "2b3dd0b54ab06c6c8e6cf617f20d5fff15ee1b71"

SHORT_URL_2 = "arolinks.com"
SHORT_API_2 = "2b3dd0b54ab06c6c8e6cf617f20d5fff15ee1b71"

SHORT_TUT = "https://t.me/How_to_Download_7x/26"

# Bot Configuration
SESSION = "yato"
TOKEN = "5717147729:AAHf-p-YAP5Oyor4xKToTZKlr9TC6Wt1JOY"
API_ID = "27353035"
API_HASH = "cf2a75861140ceb746c7796e07cbde9e"
WORKERS = 5

# Database
DB_URI = "mongodb+srv://poulomig644_db_user:d9MMUd5PsTP5MDFf@cluster0.q5evcku.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "yato"

FSUBS = [[-1001918476761, True, 10]]

DB_CHANNEL = -1001918476761

AUTO_DEL = 300

ADMINS = [1327021082, 1327021082]

DISABLE_BTN = True
PROTECT = True

# Messages Configuration
MESSAGES = {
    "START": "<b>›› ʜᴇʏ!!, {first} ~ <blockquote>ʟᴏᴠᴇ ᴘᴏʀɴʜᴡᴀ? ɪ ᴀᴍ ᴍᴀᴅᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ғɪɴᴅ ᴡʜᴀᴛ ʏᴏᴜ aʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ.</blockquote></b>",

    "FSUB": "<b><blockquote>›› ʜᴇʏ ×</blockquote>\n  ʏᴏᴜʀ ғɪʟᴇ ɪs ʀᴇᴀᴅʏ ‼️ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴜʙsᴄʀɪʙᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ, sᴜʙsᴄʀɪʙᴇ ɴᴏᴡ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ғɪʟᴇs</b>",

    "ABOUT": "<b>›› ғᴏʀ ᴍᴏʀᴇ: @Nova_Flix \n <blockquote expandable>›› ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ: <a href='https://t.me/codeflix_bots'>Cʟɪᴄᴋ ʜᴇʀᴇ</a> \n›› ᴏᴡɴᴇʀ: @ProYato\n›› ʟᴀɴɢᴜᴀɢᴇ: <a href='https://docs.python.org/3/'>Pʏᴛʜᴏɴ 3</a> \n›› ʟɪʙʀᴀରୀ: <a href='https://docs.pyrogram.org/'>Pʏʀᴏଗ୍ରାମ ᴠ2</a> \n›› ᴅାଟାବାସ୍: <a href='https://www.mongodb.com/docs/'>Mᴏଙ୍ଗୋ ᴅବ୍</a> \n›› ଡେଭଲପର୍: @cosmic_freak</b></blockquote>",

    "REPLY": "<b>For More Join - @Hanime_Arena</b>",

    "SHORT_MSG": "<b>📊 ʜᴇଏ {first}, \n\n‼️ ଗେଟ୍ ଆଲ୍ ଫାଇଲ୍ସ ଇନ୍ ଏ ସିଙ୍ଗଲ୍ ଲିଙ୍କ୍ ‼️\n\n⌯ ତୁମର ଲିଙ୍କ୍ ରେଡି ଅଛି, ଦୟାକରି ଓପେନ୍ ଲିଙ୍କ୍ ବଟନ୍ କ୍ଲିକ୍ କର।</b>",

    "START_PHOTO": "https://graph.org/file/510affa3d4b6c911c12e3.jpg",
    "FSUB_PHOTO": "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg",
    "SHORT_PIC": "https://telegra.ph/file/7a16ef7abae23bd238c82-b8fbdcb05422d71974.jpg",
    "SHORT": "https://telegra.ph/file/8aaf4df8c138c6685dcee-05d3b183d4978ec347.jpg"
}

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
