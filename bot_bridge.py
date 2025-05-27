import discord
import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 불러오기 (DISCORD_TOKEN 등)
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"  # RASA 서버 REST 엔드포인트

# 디스코드 봇의 권한(인텐트) 설정: 메시지 내용 읽기 허용
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def split_text(text: str, max_length: int = 2000) -> list:
    """
    디스코드 메시지 길이 제한(2000자)에 맞춰 텍스트를 분할하는 함수
    """
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

@client.event
async def on_ready():
    """
    봇이 정상적으로 로그인되었을 때 호출되는 이벤트 핸들러
    """
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author.bot:
        # 다른 봇이 보낸 메시지는 무시
        return

    if not client.user.mentioned_in(message):
        # 봇이 멘션되지 않은 메시지는 무시
        return

    # 멘션 부분을 제거하고 실제 질문만 추출
    clean_content = message.content.replace(client.user.mention, '').strip()
    payload = {"sender": str(message.author.id), "message": clean_content}

    # 사용자에게 답변 준비 중임을 알리는 임시 메시지 전송
    thinking_msg = await message.channel.send("💬 chat_bot이 대답 중이에요... 잠시만요오!")

    try:
        # RASA 서버에 POST 요청으로 메시지 전달
        response = requests.post(RASA_URL, json=payload)
        if response.ok:
            # RASA 응답에서 텍스트만 추출
            rasa_texts = [r["text"] for r in response.json() if "text" in r]
            if rasa_texts:
                # 여러 응답을 하나로 합치고, 길이에 따라 분할
                full_response = "\n".join(rasa_texts)
                chunks = split_text(full_response)
                
                # 첫 번째 청크는 thinking_msg를 수정해서 보여줌
                await thinking_msg.edit(content=chunks[0])
                
                # 나머지 청크는 새 메시지로 전송
                for chunk in chunks[1:]:
                    await message.channel.send(chunk)
            else:
                # RASA가 텍스트 응답을 주지 않은 경우
                await thinking_msg.edit(content="⚠️ 챗봇이 답변을 찾지 못했습니다.")
        else:
            # RASA 서버 연결 실패
            await thinking_msg.edit(content="⚠️ RASA 서버 연결에 문제가 발생했습니다.")
    except Exception as e:
        # 네트워크 등 예외 발생 시 에러 메시지 출력 및 안내
        print(f"RASA 오류: {e}")
        await thinking_msg.edit(content="🔌 챗봇 서비스가 일시적으로 중단되었습니다.")

# 디스코드 봇 실행 (토큰 필요)
client.run(DISCORD_TOKEN)
