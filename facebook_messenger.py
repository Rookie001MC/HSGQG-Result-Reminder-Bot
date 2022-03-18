from flask import Flask, Response, request
from dotenv import load_dotenv
import requests, json, os

app = Flask(__name__)

load_dotenv()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


@app.route("/")
def hello():
    return "<h1>Hello world!</h1>"


@app.route("/webhook", methods=["POST"])
def webhook_trickery():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            webhook_event = entry["messaging"][0]
            print(webhook_event)

            sender_psid = webhook_event["sender"]["id"]
            print(f"Sender PSID: {sender_psid}")

            if webhook_event["message"]:
                handle_message(sender_psid, webhook_event["message"])
            elif webhook_event["postback"]:
                handle_postback(sender_psid, webhook_event["postback"])

        return Response(response="EVENT_RECEIVED", status=200)
    else:
        return Response(status=404)


@app.route("/webhook", methods=["GET"])
def webhook_verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        print("Webhook Verified.")
        return request.args.get("hub.challenge")
    return Response(response="Wrong verify token.", status=403)


def handle_message(sender_psid, received_message):
    if received_message["text"]:
        response = {"text": f"You sent the message: ${received_message['text']}."}
        call_SendAPI(sender_psid, response)


def call_SendAPI(sender_psid, response):
    request_body = {
        "recipient": {
            "id": sender_psid,
        },
        "message": response,
    }
    try:
        r = requests.post(
            "https://graph.facebook.com/v2.6/me/messages/?access_token=" + ACCESS_TOKEN,
            json=request_body,
        )
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Message failed to send. \nError: ${err}")


if __name__ == "__main__":
    app.run(debug=True, port=1337)
