from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import FollowupAction
import os
import requests

# 여행 일정 추천을 담당하는 액션 클래스
class ActionPlanCity(Action):
    def name(self) -> Text:
        # 이 액션의 이름을 정의 (domain.yml에 등록됨)
        return "action_recommend_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict) -> List[Dict[Text, Any]]:
        # 사용자가 입력한 도시 정보를 추출
        city = next(tracker.get_latest_entity_values("city"), None)

        # 실제로는 Gemini AI에게 질문을 넘김
        dispatcher.utter_message(text="Gemini AI에게 물어볼게요!\n\n")
        # Gemini로 질문을 넘기는 액션을 이어서 실행
        return [FollowupAction("action_gemini_fallback")]

# Gemini AI를 통해 답변을 받아오는 액션 클래스
class ActionGeminiFallback(Action):
    def name(self) -> Text:
        return "action_gemini_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 사용자의 마지막 메시지(질문) 가져오기
        user_msg = tracker.latest_message.get("text", "")
        # 환경변수에서 Gemini API 키 가져오기
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        # Gemini API 호출 URL 생성
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

        # API 키가 없으면 안내 메시지
        if not gemini_api_key:
            dispatcher.utter_message(text="Gemini API 키가 설정되어 있지 않습니다.")
            return []

        # 사용자의 질문이 없으면 안내 메시지
        if not user_msg:
            dispatcher.utter_message(text="사용자 메시지가 없습니다.")
            return []

        # Gemini API에 보낼 데이터 준비
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": user_msg}]}]
        }

        try:
            # Gemini API에 POST 요청 보내기
            response = requests.post(gemini_url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                # 정상 응답이면 답변 추출
                res_json = response.json()
                gemini_answer = res_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "답변을 생성할 수 없습니다.")
                dispatcher.utter_message(text=f"Gemini의 답변: {gemini_answer}")
            else:
                # 오류 발생 시 안내
                dispatcher.utter_message(text=f"Gemini API 호출에 실패했습니다. 상태코드: {response.status_code}")
        except Exception as e:
            # 예외 발생 시 안내
            dispatcher.utter_message(text=f"Gemini API 연결 중 오류가 발생했습니다: {e}")
        return []