import discord
import requests
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

intents = discord.Intents.default()
intents.message_content = True  # 메시지 내용 읽기 권한 활성화
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:  # 봇의 메시지는 무시
        return
    
    # 멘션 확인 추가 부분
    if not client.user.mentioned_in(message):  # 봇이 멘션되지 않았으면 종료
        return
    
    # 멘션 제거 후 메시지 처리 (선택적)
    clean_content = message.content.replace(client.user.mention, '').strip()
    
    payload = {
        "sender": str(message.author.id),
        "message": clean_content  # 원본 대신 정제된 메시지 사용
    }
    
    try:
        response = requests.post(RASA_URL, json=payload)
        if response.ok:
            for r in response.json():
                if "text" in r:
                    await message.channel.send(r["text"])
        else:
            await message.channel.send("⚠️ RASA 서버 연결에 문제가 발생했습니다.")
    except Exception as e:
        print(f"RASA 오류: {e}")
        await message.channel.send("🔌 챗봇 서비스가 일시적으로 중단되었습니다.")

client.run(DISCORD_TOKEN)
