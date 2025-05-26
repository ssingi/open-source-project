import discord
import requests
from dotenv import load_dotenv
import os

# actions 폴더의 .env 파일에서 환경변수(토큰 등) 불러오기
load_dotenv(dotenv_path=os.path.join("actions", ".env"))

# 디스코드 봇 토큰과 Rasa 서버 주소를 환경변수/상수로 저장
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

# 디스코드 메시지 권한 설정
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    # 봇이 로그인되면 실행되는 부분
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    # 봇이 보낸 메시지는 무시
    if message.author.bot:
        return

    # 봇이 멘션된 메시지만 처리
    if not client.user.mentioned_in(message):
        return

    # 멘션 부분을 제거한 실제 질문만 추출
    clean_content = message.content.replace(client.user.mention, '').strip()

    # Rasa 챗봇에 보낼 데이터 준비
    payload = {
        "sender": str(message.author.id),
        "message": clean_content
    }

    # 우선 "생각 중" 메시지를 먼저 보냄
    thinking_msg = await message.channel.send("💬 chat_bot이 대답 중이에요... 잠시만요오!")

    try:
        # Rasa 챗봇에 질문을 보내고 응답 받기
        response = requests.post(RASA_URL, json=payload)
        if response.ok:
            rasa_texts = [r["text"] for r in response.json() if "text" in r]
            if rasa_texts:
                # 답변이 있으면 메시지 수정해서 보여줌
                await thinking_msg.edit(content="\n".join(rasa_texts))
            else:
                await thinking_msg.edit(content="⚠️ 챗봇이 답변을 찾지 못했습니다.")
        else:
            await thinking_msg.edit(content="⚠️ RASA 서버 연결에 문제가 발생했습니다.")
    except Exception as e:
        print(f"RASA 오류: {e}")
        await thinking_msg.edit(content="🔌 챗봇 서비스가 일시적으로 중단되었습니다.")

# 디스코드 봇 실행 (토큰 필요)
client.run(DISCORD_TOKEN)
