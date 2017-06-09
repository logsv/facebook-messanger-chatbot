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
                    if messaging_event.get("message", None) is not None:  # someone sent us a message
                        sender_id = messaging_event["sender"]["id"]
                        recipient_id = messaging_event["recipient"]["id"]
                        message_text = messaging_event["message"].get('text', 'Tell me more')  # the message's text
                        self._post_messenger(sender_id, message_text)  # reply
                    if messaging_event.get('postback', None) is not None:
                        pass
        return HttpResponse('ok', status=200)

    def _post_messenger(self, sender_id, message_text):
        """post reply on facebook"""
        params = {
            "access_token": settings.ACCESS_TOKEN #os.environ.get('PAGE_ACCESS_TOKEN')
        }
        headers = {'Content-Type': "application/json"}
        data = json.dumps({
            "recipient": {
                "id": sender_id
            },
            "message": {
                "text": message_text
            },
        })
        status = requests.post('https://graph.facebook.com/v2.6/me/messages', params=params, headers=headers, data=data)
        pprint(status.json())
