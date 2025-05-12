from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import os
from dotenv import load_dotenv
load_dotenv()

class ActionPlanTrip(Action):
    def name(self) -> Text:
        return "action_plan_trip"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city = tracker.get_slot("city")
        if not city:
            text = tracker.latest_message.get("text", "")
            for c in ["도쿄", "교토", "오사카"]:
                if c in text:
                    city = c
                    break
        if city == "도쿄":
            dispatcher.utter_message(text="도쿄 2박3일 추천 코스: 1일차-아사쿠사, 우에노, 2일차-시부야, 신주쿠, 3일차-도쿄타워, 오다이바")
        elif city == "교토":
            dispatcher.utter_message(text="교토 2박3일 추천 코스: 1일차-기온, 청수사, 2일차-금각사, 은각사, 3일차-후시미이나리, 아라시야마")
        elif city == "오사카":
            dispatcher.utter_message(text="오사카 2박3일 추천 코스: 1일차-도톤보리, 신사이바시, 2일차-유니버설 스튜디오, 3일차-오사카성, 텐노지")
        else:
            dispatcher.utter_message(text="도쿄, 교토, 오사카 중 한 도시를 말씀해 주세요!")
        return []

class ActionGeminiFallback(Action):
    def name(self) -> Text:
        return "action_gemini_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_msg = tracker.latest_message.get("text", "")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        gemini_url ="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}" \
            .replace("${GEMINI_API_KEY}", gemini_api_key)
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
            response = requests.post(gemini_url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                res_json = response.json()
                try:
                    gemini_answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                except Exception:
                    gemini_answer = str(res_json)
                dispatcher.utter_message(text=f"Gemini의 답변: {gemini_answer}")
            else:
                dispatcher.utter_message(text=f"Gemini API 호출에 실패했습니다. 상태코드: {response.status_code}")
        except Exception as e:
            dispatcher.utter_message(text=f"Gemini API 연결 중 오류가 발생했습니다: {e}")
        return []