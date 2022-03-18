from flask import Flask, Response, request
from dotenv import load_dotenv
import requests, json, os
import rss

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


def setup_information():
    request_body = {
        "get_started": {"payload": "GET_STARTED_PAYLOAD"},
        "greeting": [
            {
                "locale": "en_US",
                "text": "Just a Messenger bot for experimenting with different things.",
            },
            {
                "locale": "vi_VN",
                "text": "Một con bot Messenger để làm tí thử nghiệm. (Toàn bộ tin nhắn bằng tiếng Anh)",
            },
        ],
        "get_started": {"payload": "GET_STARTED_PAYLOAD"},
    }
    try:
        r = requests.post(
            "https://graph.facebook.com/me/messenger_profile?access_token="
            + ACCESS_TOKEN,
            json=request_body,
        )
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Message failed to send. \nError: ${err}")
        return Response(response=err, status=r.status_code)


def handle_message(sender_psid, received_message):
    if received_message["text"] == "/update":
        response = fetch_manual()
        call_SendAPI(sender_psid, response)
    if received_message["text"] == "/subscribe":
        subscribe_to_result(sender_psid)


def call_SendAPI(sender_psid, response):
    request_body = {
        "recipient": {
            "id": sender_psid,
        },
        "message": response,
    }
    try:
        r = requests.post(
            "https://graph.facebook.com/me/messages/?access_token=" + ACCESS_TOKEN,
            json=request_body,
        )
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Message failed to send. \nError: ${err}")
        return Response(response=err, status=r.status_code)


def handle_postback(sender_psid, received_postback):
    payload = received_postback["payload"]

    if payload == "GET_STARTED_PAYLOAD":
        response = {
            "text": "Hi there!\n\nThis is just a messenger bot used for any experimentation that I may come up with.\n\nSo far it has only one use, to allow notification of the HSGQG result."
        }
    call_SendAPI(sender_psid, response)


def subscribe_to_result(sender_psid):
    pass  # This is mainly used on repl.it, so I'll be using the replit package instead.


def fetch_manual():
    rss.main()
    with open("result.json", "r") as result_file:
        result_info = json.load(result_file)
    updated_time = result_info["updated_time"]
    if result_info["result"] == 0:
        message = {
            "text": f"Last updated: {updated_time}.\n\nResult not yet available."
        }
        return message
    else:
        message = "Result is available."
        post_url = result_info["url"]
        response = {
            "text": f"Last updated:{updated_time}\n\n{message} \n\nSee the results here: {post_url}"
        }
        return response


def fetch_auto():
    rss.main()
    with open("result.json", "r") as result_file:
        result_info = json.load(result_file)
    updated_time = result_info["updated_time"]
    if result_info["result"] == 1:
        post_url = result_info["url"]
        message = {
            "text": f"Last updated:{updated_time}\n\nResult is available.\n\nSee the results here: {post_url}"
        }
        call_SendAPI()


if __name__ == "__main__":
    app.run(debug=True, port=1337)
