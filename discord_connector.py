# import os
# import sys
# from dotenv import load_dotenv
# import requests  # 추가
# from rasa.core.channels.channel import InputChannel, UserMessage
# from sanic import Blueprint
# import asyncio
# from discord.ext import commands
# import discord

# load_dotenv()

# class DiscordInput(InputChannel):
#     @classmethod
#     def name(cls):
#         return "discord_custom"

#     def __init__(self):
#         self.token = os.getenv("DISCORD_TOKEN")
#         self.bot_user_id = int(os.getenv("DISCORD_BOT_USER_ID"))
#         self.rasa_url = "http://localhost:5005/webhooks/rest/webhook"

#     def blueprint(self, on_new_message):
#         bp = Blueprint("discord_webhook", __name__)
#         intents = discord.Intents.all()
#         bot = commands.Bot(command_prefix="!", intents=intents)

#         @bot.event
#         async def on_ready():
#             print(f"{bot.user} has connected to Discord!")

#         @bot.event
#         async def on_message(message):
#             if message.author == bot.user:
#                 return

#             if bot.user not in message.mentions:
#                 return

#             # 메시지 처리
#             clean_text = message.clean_content.replace(f"<@{self.bot_user_id}>", "").strip()
            
#             # Rasa로 전송
#             payload = {
#                 "sender": str(message.author.id),
#                 "message": clean_text
#             }
#             response = requests.post(self.rasa_url, json=payload)

#             # 응답 처리
#             if response.ok:
#                 for r in response.json():
#                     await message.channel.send(r['text'])
#             else:
#                 await message.channel.send("오류 발생")

#         loop = asyncio.get_event_loop()
#         loop.create_task(bot.start(self.token))

#         return bp
