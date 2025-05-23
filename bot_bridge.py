import discord
import requests
import asyncio
import os
from dotenv import load_dotenv  # .env 파일에서 환경변수 로드

load_dotenv()  # 환경변수 로드

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # Discord 봇 토큰
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"  # Rasa REST 엔드포인트(챗봇 서버의 주소)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
# 사용자가 메시지를 보내면 챗봇에게 전달하고, 챗봇의 답변을 받아 다시 사용자에게 보내줍니다.
async def on_message(message):
    if message.author.bot:
        return

    # Discord 메시지를 Rasa로 전달
    payload = {
        "sender": str(message.author.id),
        "message": message.content
    }
    response = requests.post(RASA_URL, json=payload)

    # Rasa 응답을 Discord로 전송
    if response.ok:
        responses = response.json()
        for r in responses:
            if "text" in r:
                await message.channel.send(r["text"])
    else:
        await message.channel.send("챗봇 응답 오류가 발생했습니다.")

client.run(DISCORD_TOKEN)
