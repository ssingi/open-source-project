from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from typing import Text, Dict, Any, List  
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re

# .env 파일에서 API 키 불러오기
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Gemini Pro 모델 설정
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# ✅ 중복 제거 함수
def remove_redundant_lines(text):
    seen = set()
    result = []
    for line in text.strip().split('\n'):
        line_clean = line.strip()
        if line_clean and line_clean not in seen:
            seen.add(line_clean)
            result.append(line_clean)
    return '\n'.join(result)

# ✅ Gemini 응답 정제 및 장소/설명 추출 함수
def extract_places(text: str) -> list:
    """
    Gemini 응답에서 '장소: 설명' 형태로 추출
    """
    lines = text.strip().split('\n')
    results = []
    for line in lines:
        match = re.match(r"^\s*\d+[\.\)]\s*(.+?)\s*[-–—:]\s*(.+)$", line)
        if match:
            place = match.group(1).strip(" *")
            desc = match.group(2).strip()
            results.append((place, desc))
    return results


class ActionGeminiFallback(Action):
    def name(self) -> Text:
        return "action_gemini_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 슬롯에서 location과 preference 가져오기
        location = tracker.get_slot("location") or "일본"
        preference = tracker.get_slot("preference") or "관광"

        # ActionRecommendPlace의 프롬프트를 기반으로 생성
        prompt = f"""
        당신은 일본 여행 전문가입니다.
        사용자가 일본 {location}에서 {preference}를 즐기고 싶어 해요.

        ✅ 아래 기준을 엄격히 지켜서 추천해 주세요:
        1. **'{location}' 내에서만** 추천 (예: '{location}' 요청 시 '{location}' 외 지역은 절대 포함 금지)
        2. 추천 장소는 3~5곳, 장소 이름과 간단한 설명
        3. 불필요한 지역 설명, 서론, 여행코스 추천은 생략
        4. **'{location}'이라는 지역명을 명시한 장소만 포함** (예: '{location} 성', '{location} 도톤보리' 등)

        아래 형식으로 답변해 주세요:

        1. 장소명 – 한 줄 설명
        2. 장소명 – 한 줄 설명
        ...
        """

        try:
            # Gemini 모델을 사용하여 응답 생성
            response = model.generate_content(prompt)
            cleaned_text = remove_redundant_lines(response.text)
            places = extract_places(cleaned_text)

            if not places:
                dispatcher.utter_message(text="추천 장소를 정리하는 데 어려움이 있었어요. 텍스트로 전체 응답을 보여드릴게요:")
                dispatcher.utter_message(text=cleaned_text)
                return []

            # ✅ 카드 스타일로 출력
            dispatcher.utter_message(text=f"🗾 {location}에서 즐길 수 있는 {preference} 장소 추천:\n")
            for place, desc in places:
                dispatcher.utter_message(text=f"🏯 *{place}*\n{desc}\n")

        except Exception as e:
            dispatcher.utter_message(text="죄송해요. 여행지를 추천하는 중 오류가 발생했어요.")
            print("Gemini 오류:", e)

        return []
    
# action_plan_city
class ActionPlanCity(Action):
    def name(self) -> Text:
        return "action_plan_city"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = next(tracker.get_latest_entity_values("city"), None)

        if not city:
            dispatcher.utter_message(text="어느 도시의 일정이 궁금하신가요?")
            return []

        city = city.strip().lower()

        itineraries = {
            "도쿄": "도쿄 일정: 시부야, 아사쿠사, 긴자 쇼핑 등 3일 코스 추천!",
            "오사카": "오사카 일정: 도톤보리, 오사카성, 유니버설 스튜디오 등 추천!",
            "교토": "교토 일정: 아라시야마, 기온 거리, 후시미 이나리 신사 추천!"
        }

        response = itineraries.get(city, f"{city}에 대한 여행 정보가 아직 준비되지 않았어요.")
        dispatcher.utter_message(text=response)
        return []