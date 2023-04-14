# (c) 2022-2023, Akkil M G (https://github.com/HeimanPictures)
# License: GNU General Public License v3.0

import os
import motor.motor_asyncio

DOMAIN = os.getenv("DOMAIN")

# MongoDB connection
MONGODB_NAME = "quickly" # os.getenv("MONGODB_NAME")
MONGODB_COL = "quickly" # os.getenv("MONGODB_COL")
MONGODB_URL = os.getenv("MONGODB_URL")
mongoClient =  motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
mongodb = mongoClient[MONGODB_NAME][MONGODB_COL]

# Chat ID
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
CHAT_ID = str(os.getenv("CHAT_ID"))

# Report
PASS = str(os.getenv("PASS"))
