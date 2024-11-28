#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Telegram Channel: linux_termux_ch

BOT_TOKEN = ""
DBS_FILE_PATH = "my/folder"

from src.phub import ( Client, Quality )
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ( Message, InlineKeyboardButton, InlineKeyboardMarkup )
from json import ( loads, dumps )
import sqlite3
import os

if not DBS_FILE_PATH.strip() == "":
    if not os.path.exists(DBS_FILE_PATH):
        os.mkdir(DBS_FILE_PATH)
else:
    DBS_FILE_PATH = "."

DBS_FILE_PATH += "/mydbs.db"

class Bases(object):
    def __init__(self):
        self.controller = sqlite3.connect(DBS_FILE_PATH, check_same_thread=False)
        self.setup()

    def setup(self):
        self.controller.execute(
            """
            CREATE TABLE IF NOT EXISTS user_videos (
                user_id TEXT PRIMARY KEY,
                user_videos TEXT
            )
            """
        )

    async def doesExist(self, user_id: str):
        for user in self.controller.execute("SELECT * FROM user_videos").fetchall():
            if user[0] == user_id:
                return { "status": "OK", "user_id": user_id, "user": loads(user[1]) }
            
        return { "status": "INVALID_USER_ID" }
    
    async def getVideos(self, user_id: str):
        status = await self.doesExist(user_id)

        if status['status'] == "OK":
            return { "status": "OK", "videos": loads(status['user']) }
        else: return status

    async def add(
        self,
        user_id: str
    ) -> dict:
        
        ver = await self.doesExist(user_id)

        if ver['status'] == "OK":
            return { "status": "EXISTS_USER" }
        
        self.controller.execute("INSERT INTO user_videos (user_id, user_videos) VALUES (?, ?)", (user_id, dumps([])))
        self.controller.commit()

        return { "status": "OK" }
    
    async def push(
        self,
        user_id: str,
        objext: dict
    ) -> str:
        
        ver = await self.getVideos(user_id)

        if ver['status'] == "OK":
            ver['videos'].append(objext)
            self.controller.execute("UPDATE user_videos SET user_videos = ? WHERE user_id = ?", (ver['videos'], user_id))
            self.controller.commit()
        
        else:return ver
    
def createString(string: str) -> str:
    string = string.lower()
    return string.translate(string.maketrans("qwertyuiopasdfghjklzxcvbnm-012345678", "Qᴡᴇʀᴛʏᴜɪᴏᴘᴀꜱᴅꜰɢʜᴊᴋʟᴢxᴄᴠʙɴᴍ-𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖"))
    
bot = AsyncTeleBot(BOT_TOKEN)
sql = Bases()
client = Client()
user_urls = {}

async def download(user_id: str):
    try:
        user = user_urls[user_id]
        url = user['url']
        qual = user['quality']

        video = client.get(url)
        structure = {
            "quality": qual.value,
            "title": video.title,
            "views": video.views,
            "likes": video.likes.up,
            "author": video.author,
            "duration": video.duration,
            "id": video.id,
            "url": video.url,
            "tags": video.tags,
            "date": video.date
        }

        await sql.push(user_id, structure)
        return { "status": "OK", "path": video.download("."), "structure": structure }
    
    except Exception as error:
        return { "status": "ERROR", "message": str(error) }

@bot.message_handler(content_types=['text'], chat_types=['private', 'supergroup'])
async def onMessages(message: Message):
    user_ver = await sql.doesExist(message.from_user.id)

    if not user_ver['status'] == "OK":
        await sql.add(message.from_user.id)

    if message.text in ( "/start", "/help" ):
        start_markup = InlineKeyboardMarkup()

        start_markup.add(
            InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ ᴠɪᴅᴇᴏ", callback_data="DownloadVideo")
        )

        start_markup.add(
            InlineKeyboardButton("ɢᴇᴛ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ᴠɪᴅᴇᴏꜱ", callback_data="GetVideos")
        )

        await bot.reply_to(message, createString("welcome - choose an option"), reply_markup=start_markup)

    elif message.text.startswith("/catch"):
        link = message.text[6:].strip()

        if not link.startswith("https://www.pornhub.com/view_video.php?viewkey="):
            await bot.reply_to(message, createString("invalid url"))
        
        else:
            user_urls[message.from_user.id] = {}
            user_urls[message.from_user.id]['url'] = link

            qup = InlineKeyboardMarkup()
            qup.add(
                InlineKeyboardButton(createString("best"), callback_data="BestQuality")
            )
            qup.add(
                InlineKeyboardButton(createString("half"), callback_data="HalfQuality")
            )
            qup.add(
                InlineKeyboardButton(createString("worst"), callback_data="WorstQuality")
            )

            await bot.reply_to(message, createString("select a quality"), reply_markup=qup)
            #Quality(['best', 'half', 'worst'])

@bot.callback_query_handler(func=lambda call: True)
async def onQuerys(call):
    if call.data == "DownloadVideo":
        await bot.reply_to(call.message, createString("send your video link infront of /catch -> /catch LINK"))
    
    elif call.data == "BestQuality":
        user_urls[call.message.from_user.id]['quality'] = Quality("best").BEST
        download(call.message.from_user.id)

    elif call.data == "HalfQuality":
        user_urls[call.message.from_user.id]['quality'] = Quality("half").HALF
        download(call.message.from_user.id)

    elif call.data == "WorstQuality":
        user_urls[call.message.from_user.id]['quality'] = Quality("worst").WORST
        download(call.message.from_user.id)