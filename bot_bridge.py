import discord
import requests
import asyncio
import os
from dotenv import load_dotenv  # 추가

load_dotenv()  # .env 파일 로드

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # .env에서 토큰 불러오기
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        return

    payload = {
        "sender": str(message.author.id),
        "message": message.content
    }
    response = requests.post(RASA_URL, json=payload)

    if response.ok:
        responses = response.json()
        for r in responses:
            if "text" in r:
                await message.channel.send(r["text"])
    else:
        await message.channel.send("챗봇 응답 오류가 발생했습니다.")

client.run(DISCORD_TOKEN)
