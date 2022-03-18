from flask import Flask, Response, request
from dotenv import load_dotenv
import requests, json, os

app = Flask(__name__)

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
        return Response(response="EVENT_RECEIVED", status=200)
    else:
        return Response(status=404)


@app.route("/webhook", methods=["GET"])
def webhook_verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        print("Webhook Verified.")
        return request.args.get("hub.challenge")
    return Response(response="Wrong verify token.", status=403)


if __name__ == "__main__":
    app.run(debug=True, port=1337)
