from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import FollowupAction
import os
import requests


# ✅ 특정 도시의 여행 일정을 추천하는 액션
# ActionPlanCity, 사용자가 "도쿄 일정 알려줘"처럼 특정 도시의 여행 일정을 물어보면, 미리 준비된 일정을 답변합니다.

# ✅ 기본 여행 일정 제공 Action

class ActionPlanCity(Action):
    def name(self) -> Text:
        return "action_recommend_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:


        # 사용자가 입력한 도시 엔티티 추출
        city = next(tracker.get_latest_entity_values("city"), None)

        # 지원하는 도시와 추천 일정 사전 정의

        city = next(tracker.get_latest_entity_values("city"), None)


        supported_cities = {
            "도쿄": "도쿄 2박3일 추천 코스: 1일차-아사쿠사, 우에노, 2일차-시부야, 신주쿠, 3일차-도쿄타워, 오다이바",
            "오사카": "오사카 2박3일 추천 코스: 1일차-도톤보리, 신사이바시, 2일차-유니버설 스튜디오, 3일차-오사카성, 텐노지",
            "교토": "교토 2박3일 추천 코스: 1일차-기온, 청수사, 2일차-금각사, 은각사, 3일차-후시미이나리, 아라시야마"
        }


        # 도시 정보가 없으면 Gemini로 fallback


        if not city:
            dispatcher.utter_message(text="도시 정보가 없습니다. 죄송해요, 그 질문에는 바로 답변드리기 어려워요. Gemini AI에게 물어볼게요!")
            return [FollowupAction("action_gemini_fallback")]

        city = city.strip()


        # 지원 도시면 추천 일정 안내

        if city in supported_cities:
            dispatcher.utter_message(text=supported_cities[city])
            return []
        else:

            # 지원하지 않는 도시는 Gemini로 넘김
            return [FollowupAction("action_gemini_fallback")]

# ✅ Gemini API를 통해 답변 생성하는 액션

            # 지원하지 않는 도시는 fallback으로 넘김
            return [FollowupAction("action_gemini_fallback")]

# ✅ Gemini를 통한 장소 추천 Action

class ActionGeminiFallback(Action):
    def name(self) -> Text:
        return "action_gemini_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 사용자의 마지막 메시지 추출

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

        return []

