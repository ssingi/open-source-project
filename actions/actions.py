from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import FollowupAction
import os
import requests

# 텍스트 2000자 제한에 맞춰 분할하는 함수
def split_text(text: str, max_length: int = 2000) -> List[str]:
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# 해당 도시의 여행 일정 제공 Action 클래스
class ActionPlanCity(Action):
    def name(self) -> Text:
        return "action_recommend_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Gemini AI에게 물어볼게요!\n\n")
        return [FollowupAction("action_gemini_fallback")]

# Gemini를 통한 장소 추천 Action (수정 버전)
class ActionGeminiFallback(Action):
    def name(self) -> Text:
        return "action_gemini_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 사용자의 마지막 메시지(질문) 추출
        user_msg = tracker.latest_message.get("text", "")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

        if not gemini_api_key:
            dispatcher.utter_message(text="⚠️ Gemini API 키 오류")
            return []

        if not user_msg:
            dispatcher.utter_message(text="⚠️ 유효한 질문이 없습니다")
            return []

        # Gemini API 요청 헤더 및 데이터 구성
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": user_msg}]}]}

        try:
            # Gemini API에 POST 요청
            response = requests.post(gemini_url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                # 응답에서 답변 텍스트 추출
                res_json = response.json()
                gemini_answer = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "답변을 생성할 수 없습니다.")
                
                # 답변이 2000자를 넘을 경우 분할하여 전송 (디스코드 메시지 제한 대응)
                chunks = split_text(f"Gemini의 답변: {gemini_answer}")
                for chunk in chunks:
                    dispatcher.utter_message(text=chunk)
                    
            else:
                error_msg = f"⚠️ API 호출 실패 (코드: {response.status_code})"
                dispatcher.utter_message(text=error_msg[:2000])
                
        except Exception as e:
            error_msg = f"🔌 연결 오류: {str(e)}"
            dispatcher.utter_message(text=error_msg[:2000])
            
        return []
