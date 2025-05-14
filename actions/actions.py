from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import os
import requests

# ✅ 기본 여행 일정 제공 Action
class ActionPlanCity(Action):
    def name(self) -> Text:
        return "action_recommend_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:

        city = next(tracker.get_latest_entity_values("city"), None)

        if not city:
            dispatcher.utter_message(text="어느 도시의 일정이 궁금하신가요?") # text 바꾸기
            return []

        city = city.strip().lower()

        itineraries = {
            "도쿄": "도쿄 2박3일 추천 코스: 1일차-아사쿠사, 우에노, 2일차-시부야, 신주쿠, 3일차-도쿄타워, 오다이바",
            "오사카": "교토 2박3일 추천 코스: 1일차-기온, 청수사, 2일차-금각사, 은각사, 3일차-후시미이나리, 아라시야마",
            "교토": "오사카 2박3일 추천 코스: 1일차-도톤보리, 신사이바시, 2일차-유니버설 스튜디오, 3일차-오사카성, 텐노지"
        }

        response = itineraries.get(city, f"{city}에 대한 여행 정보가 아직 준비되지 않았어요.")
        dispatcher.utter_message(text=response)
        return []

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
            response = requests.post(gemini_url, headers=headers, json=data, timeout=30)  # timeout을 30초로 증가
            if response.status_code == 200:
                res_json = response.json()
                gemini_answer = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "답변을 생성할 수 없습니다.")
                dispatcher.utter_message(text=f"Gemini의 답변: {gemini_answer}")
            else:
                dispatcher.utter_message(text=f"Gemini API 호출에 실패했습니다. 상태코드: {response.status_code}")
        except Exception as e:
            dispatcher.utter_message(text=f"Gemini API 연결 중 오류가 발생했습니다: {e}")
        return []