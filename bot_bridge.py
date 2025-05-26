import discord
import requests
from dotenv import load_dotenv
import os

# actions 폴더의 .env 파일을 명시적으로 로드
load_dotenv(dotenv_path=os.path.join("actions", ".env"))

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
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

    if not client.user.mentioned_in(message):
        return

    clean_content = message.content.replace(client.user.mention, '').strip()

    payload = {
        "sender": str(message.author.id),
        "message": clean_content
    }

    # 1. 먼저 "생각 중이에요" 메시지를 보냄
    thinking_msg = await message.channel.send("💬 chat_bot이 대답 중이에요... 잠시만요오!")

    try:
        # 2. 실제 응답을 받아옴
        response = requests.post(RASA_URL, json=payload)
        if response.ok:
            rasa_texts = [r["text"] for r in response.json() if "text" in r]
            if rasa_texts:
                # 3. 메시지 수정(편집)으로 답변 표시
                await thinking_msg.edit(content="\n".join(rasa_texts))
            else:
                await thinking_msg.edit(content="⚠️ 챗봇이 답변을 찾지 못했습니다.")
        else:
            await thinking_msg.edit(content="⚠️ RASA 서버 연결에 문제가 발생했습니다.")
    except Exception as e:
        print(f"RASA 오류: {e}")
        await thinking_msg.edit(content="🔌 챗봇 서비스가 일시적으로 중단되었습니다.")

client.run(DISCORD_TOKEN)
