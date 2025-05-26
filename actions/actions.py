from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import FollowupAction
import os
import requests

# ✅ 기본 여행 일정 제공 Action
class ActionPlanCity(Action):
    def name(self) -> Text:
        return "action_recommend_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:

        # 도시 엔티티 추출
        city = next(tracker.get_latest_entity_values("city"), None)

        # 무조건 Gemini로 폴백
        dispatcher.utter_message(text="Gemini AI에게 물어볼게요!\n\n")
        return [FollowupAction("action_gemini_fallback")]

# ✅ Gemini를 통한 장소 추천 Action
class ActionGeminiFallback(Action):
    def name(self) -> Text:
        return "action_gemini_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_msg = tracker.latest_message.get("text", "")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

        if not gemini_api_key:
            dispatcher.utter_message(text="Gemini API 키가 설정되어 있지 않습니다.")
            return []

        if not user_msg:
            dispatcher.utter_message(text="사용자 메시지가 없습니다.")
            return []

        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": user_msg}]}]
        }

        try:
            response = requests.post(gemini_url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                res_json = response.json()
                gemini_answer = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "답변을 생성할 수 없습니다.")
                dispatcher.utter_message(text=f"Gemini의 답변: {gemini_answer}")
            else:
                dispatcher.utter_message(text=f"Gemini API 호출에 실패했습니다. 상태코드: {response.status_code}")
        except Exception as e:
            dispatcher.utter_message(text=f"Gemini API 연결 중 오류가 발생했습니다: {e}")
        return []
