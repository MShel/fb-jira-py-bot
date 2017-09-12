from transport.AbstractTransport import AbstractTransport
import requests
from flask import Flask, request
from flask.views import View
from Router import Router
import json
from flask_restful import Resource


class Facebook(AbstractTransport):
    verify_token = None

    access_token = 'test'

    access_point_root = None

    ENDPOINTS_TO_ADD = ["/privacy", "/webhook"]

    def __init__(self, router: Router, access_token: str, verify_token: str, access_point_root: str):
        self.access_token = access_token
        self.verify_token = verify_token
        self.access_point_root = access_point_root
        self.router = router

    def get_end_points_to_add(self):
        return self.ENDPOINTS_TO_ADD

class FacebookEndPoint(Resource):

    fb = None

    app = None

    methods = ['GET', 'POST']


    def __init__(self, fb: Facebook, app: Flask):
        self.fb = fb
        self.app = app

    def get(self):
        print(request.path)
        return self.app.send_static_file('privacy.html')

    def test(self, param=None):
        print(self.fb)
        print(request.path)
        return request

    def webhook(self) -> tuple:
        data = request.get_json()
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]
                        messageGenerator = self.get_reply_message(sender_id, messaging_event["message"]["text"].lower())
                        for message in messageGenerator:
                            self.send_message(sender_id, message)

        return "ok", 200

    def get_privacy(self):
        self.app.send_static_file('privacy.html')

    def verify(self) -> tuple:
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
            if not request.args.get("hub.verify_token") == self.verify_token:
                return "Verification token mismatch", 403
            return request.args["hub.challenge"], 200

        return "We Goy to FB transport!", 200

    def send_message(self, recipient_id: int, message_text: int):
        params = {
            "access_token": self.access_token
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text
            }
        })
        requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
