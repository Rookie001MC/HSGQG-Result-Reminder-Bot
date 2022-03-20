from flask import Flask, Response, request, render_template
from dotenv import load_dotenv
import requests, json, os
import rss
from threading import Thread

app = Flask(__name__)

load_dotenv()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

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
    if received_message["text"] == "/update":
        response = fetch_if_result_posted()
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
            "https://graph.facebook.com/me/messages/?access_token=" + ACCESS_TOKEN,
            json=request_body,
        )
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Message failed to send. \nError: ${err}")
        return Response(response=err, status=r.status_code)


def handle_postback(sender_psid, received_postback):
    response = {
        "text": "Sadly not implemented. I'll finish this whenever I'm not lazy."
    }
    call_SendAPI(sender_psid, response)


def fetch_if_result_posted():
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

def keep_alive() -> None:
    """ Wraps the web server run() method in a Thread object and starts the web server. """
    def run() -> None:
        app.run(host = '0.0.0.0', port = 1337)
    thread = Thread(target = run)
    thread.start()

if __name__ == "__main__":
    keep_alive()