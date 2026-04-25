import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("8485266843:AAHHNIPcn9Hgf_iOQDEL0hT105goEwC6-CM")
ADMIN_IDS = list(map(int, os.getenv("6551375195", "0").split(",")))
DB_PATH = "ilc.db"
TEMPLATE_PATH = "Ariza_Namuna.docx"
