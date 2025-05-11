# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, Restarted
import requests
import aiohttp
import asyncio
from sqlalchemy import create_engine

async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.json()

class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []

class ActionGetRealTimeData(Action):
    def name(self) -> Text:
        return "action_get_realtime_data"  # 액션 고유 ID

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # 1. 슬롯 값 추출
        location = tracker.get_slot("location")
        
        # 2. 외부 API 호출 (예: OpenWeatherMap)
        api_key = "YOUR_API_KEY"  # 여기에 실제 API 키를 입력하세요.
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                
                # 3. 동적 응답 생성
                message = f"{location}의 현재 온도는 {temp}°C, 날씨는 {description}입니다."
                dispatcher.utter_message(text=message)
                
                # 4. 슬롯 업데이트 (선택적)
                return [SlotSet("last_weather", message)]
            else:
                dispatcher.utter_message(text="날씨 정보를 가져오지 못했습니다.")
        except Exception as e:
            dispatcher.utter_message(text="서버 연결에 문제가 발생했습니다.")
        
        return []

class ActionAskAdditionalInfo(Action):
    def name(self):
        return "action_ask_additional_info"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="추가 정보를 알려주세요.")
        return []

class ActionWelcome(Action):
    def name(self):
        return "action_welcome"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="환영합니다! 무엇을 도와드릴까요?")
        return []

class ActionExampleFollowup(Action):
    def name(self):
        return "action_example_followup"

    def run(self, dispatcher, tracker, domain):
        # FollowupAction을 이용한 연속 액션 실행
        return [FollowupAction("action_ask_additional_info")]

class ActionExampleRestart(Action):
    def name(self):
        return "action_example_restart"

    def run(self, dispatcher, tracker, domain):
        # Restarted()로 대화 초기화 후 액션 연결
        return [Restarted(), FollowupAction("action_welcome")]

class ActionAsyncData(Action):
    def name(self) -> str:
        return "action_async_data"

    async def run(self, dispatcher: CollectingDispatcher, tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            try:
                data = await fetch_data(session, "https://api.example.com/data")
                dispatcher.utter_message(text=f"비동기 결과: {data['value']}")
            except Exception as e:
                dispatcher.utter_message(text="데이터를 가져오는 중 오류가 발생했습니다.")
        return []

class ActionDBQuery(Action):
    def name(self) -> str:
        return "action_db_query"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain: Dict[str, Any]) -> List[Dict[str, Any]]:
        # SQLite 데이터베이스 연결
        engine = create_engine('sqlite:///travel.db')
        city = tracker.get_slot("city")  # 슬롯에서 도시 정보 가져오기

        if not city:
            dispatcher.utter_message(text="도시 정보를 입력해주세요.")
            return []

        try:
            with engine.connect() as conn:
                # 데이터베이스에서 명소 조회
                result = conn.execute("SELECT name FROM attractions WHERE city=?", (city,))
                attractions = [row[0] for row in result]

                if attractions:
                    dispatcher.utter_message(text=f"{city}의 추천 명소: {', '.join(attractions)}")
                else:
                    dispatcher.utter_message(text=f"{city}에 대한 추천 명소 정보를 찾을 수 없습니다.")
        except Exception as e:
            dispatcher.utter_message(text="데이터베이스 조회 중 오류가 발생했습니다.")
        
        return []
