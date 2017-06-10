# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import json
from pprint import pprint

import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import View

logger = logging.getLogger('django') # logger

# Create your views here.

class MessangerBot(View):
    """Facebbok messanger bot for page chatbotstory """

    def __init__(self):
        self.params = {
            "access_token": settings.ACCESS_TOKEN #os.environ.get('PAGE_ACCESS_TOKEN')
        }
        self.headers = {'Content-Type': "application/json"}
        self.graph_url = 'https://graph.facebook.com/v2.6/me/messages'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(MessangerBot, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.GET.get('hub.mode', '') == 'subscribe' and request.GET.get('hub.challenge', False):
            if not request.GET.get('hub.verify_token', '') == settings.VERIFY_TOKEN:
                return HttpResponse('Verification failed', status=403)
            return HttpResponse(request.GET.get('hub.challenge'), status=200)
        return HttpResponse('ok', status=200)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]
                    if messaging_event.get("message", None) is not None:  # someone sent us a message
                        message_text = messaging_event["message"].get('text', 'Tell me more')  # the message's text
                        self._post_messange(sender_id, message_text)  # reply
                    if messaging_event.get('postback', None) is not None:
                        postback = messaging_event.get('postback')
                        payload = postback.get('payload', '')
                        self._post_postback(sender_id, payload)
        return HttpResponse('ok', status=200)

    def _post_postback(self, sender_id, payload):
        data = {
            'recipient': {'id': sender_id},
            'message': {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'button',
                        'text': 'Hi, How can we help you?',
                        'buttons': [
                            {
                                'type': 'web_url',
                                'url': 'https://codeifyoucansolve.wordpress.com',
                                'title': 'Code If You Can Solve'
                            },
                            {
                                'type': 'postback',
                                'title': 'Start Chating',
                                'payload': "start-chating"
                            },
                        ]
                    }
                }
            }
        }
        data = json.dumps(data)
        status = requests.post(self.graph_url, params=self.params, headers=self.headers, data=data)
        pprint(status.json())

    def _post_messange(self, sender_id, message_text):
        """post reply on facebook"""
        data = json.dumps({
            "recipient": {
                "id": user_id
            },
            "message": {
                "text": message_text
            },
        })
        status = requests.post(self.graph_url, params=self.params, headers=self.headers, data=data)
        pprint(status.json())
