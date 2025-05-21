from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    user_msg = data['userRequest']['utterance']
    
    # Rasa와 연결
    response = requests.post("http://localhost:5005/webhooks/rest/webhook", json={"sender": "user", "message": user_msg})
    bot_reply = response.json()[0]['text']

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": bot_reply}}]
        }
    })

if __name__ == "__main__":
    app.run(port=8000)
