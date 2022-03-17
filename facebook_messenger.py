from flask import Flask, Response, request
from dotenv import load_dotenv
import requests, json, os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


@app.route("/")
def hello():
    return "<h1>Hello world!</h1>"


@app.route("/webhook", methods=["GET"])
def verify_fb_token():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid verification token."


@app.route("/webhook", methods=["POST"])
def webhook_action():
    data = json.loads(request.data.decode("UTF-8"))
    for entry in data["entry"]:
        user_message = entry["messaging"][0]["message"]["text"]
        user_id = entry["messaging"][0]["sender"]["id"]
        response = {"recipient": {"id": user_id}, "message": {}}

        response["message"]["text"] = handle_message(user_id, user_message)

        r = requests.post(
            "https://graph.facebook.com/me/messages/?access_token=" + ACCESS_TOKEN,
            json=response,
        )
    return Response(response="EVENT RECEIVED", status=200)


@app.route("/webhook_test", methods=["POST"])
def webhook_dev():
    data = json.loads(request.data.decode("UTF-8"))
    user_message = data["entry"][0]["messaging"][0]["message"]["text"]
    user_id = data["entry"][0]["messaging"][0]["sender"]["id"]
    response = {
        "recipient": {"id": user_id},
        "message": {"text": handle_message(user_id, user_message)},
    }
    return Response(
        response=json.dumps(response), status=200, mimetype="application/json"
    )


def handle_message(user_id, user_message):
    if user_message == "Update":
        return "Yep: " + user_message


if __name__ == "__main__":
    app.run(debug=True, port=1337)
