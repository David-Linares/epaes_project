import json

import requests
from django.db import connection
from gtts import gTTS
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings


class WebhookResponse(APIView):

    def get(self, request):
        mode = request.query_params.get("hub.mode", False)
        challenge = request.query_params.get("hub.challenge", False)
        verify_token = request.query_params.get("hub.verify_token", False)
        if mode == 'subscribe' and verify_token == settings.CONSTANTS['VERIFY_TOKEN']:
            print("Validate token verify")
            return Response(json.loads(challenge), status=200)
        else:
            print("Please Validate the token")
            return Response(status=403)

    # Recibe cualquier petición de FB
    def post(self, request):
        data = request.data
        print(data)
        if (data['object'] == 'page'):
            entry = data['entry']
            for i in entry:
                messaging = i['messaging']
                for j in messaging: # Evalúa los datos que llegan de la petición de FB
                    if "message" in j: # Si escriben un mensaje
                        self.receive_message(j)
                    elif "postback" in j: # Si oprimen un botón
                        self.get_menus_db(j['postback']['payload'], j['sender']['id'])

        else:
            pass
        return Response(status=200)

    def receive_message(self, event):
        print("data %s " % str(event))
        sender_id = int(event['sender']['id'])
        recipient_id = int(event['recipient']['id'])
        message = event['message']
        time_message = int(event['timestamp'])

        message_id = message['mid']
        message_text = message.get('text', None)
        message_attachments = message.get("attachments", None)

        if (message_text):
            self.get_menus_db(1, sender_id)
        elif (message_attachments):
            for at in message_attachments:
                if at['type'] == "audio": # Respondió con un mensaje de audio.
                    self.send_text_message(sender_id, "Muy buen intento!! Sigue probando y pronto mejorarás bastante tú pronunciación!!" , 0)


    def get_menus_db(self, id_menu, sender_id):
        print("id_menu %s" % id_menu)
        print("sender_id %s" % sender_id)
        try:
            query = "select t.tipo_msj, m.* from mensajes as m join tipos_msj as t on m.tipo_contenido = t.id_tipo where id_msj = %d" % int(id_menu)
            with connection.cursor() as cursor:
                cursor.execute(query);
                data = cursor.fetchall()
                print(data)
                for d in data:
                    self.send_text_message(sender_id, d[4], d[0], d[1])
        except Exception as e:
            print(e)

    def get_submenus_db(self, parent_id):
        try:
            query = "select m.* from mensajes as m where parent_msj = %d" % int(parent_id)
            with connection.cursor() as cursor:
                cursor.execute(query);
                data = cursor.fetchall()
                print(data)
                return data
        except Exception as e:
            print(e)

    def send_text_message(self, sender_id, message_text, type_content, menu_id=None):
        print("type content %s " % type_content)
        if type_content == "Button":
            message_data = {
                "recipient": {
                    "id": sender_id
                },
                "message": {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "button",
                            "text": message_text,
                            "buttons": [

                            ]
                        }
                    }
                }
            }
            return_data = self.get_submenus_db(menu_id)
            print("send_text_message - return data %s" % str(return_data))
            for d in return_data:
                message_data['message']['attachment']['payload']['buttons'].append({"type": "postback", "title": d[3], "payload": str(d[5])})
            print(message_data)
            self.call_send_api(message_data)
        elif type_content == 4:
            text = gTTS(text=message_text, lang='es')
            audio_name = "/static/audios/audio_%s.mp3" % (menu_id)
            text.save(settings.BASE_DIR + "" + audio_name)
            message_data = {
                "recipient":{
                    "id": sender_id
                },
                "message":{
                    "attachment":{
                        "type":"audio",
                        "payload":{
                            "url":"https://0313423d.ngrok.io%s" % audio_name
                        }
                    }
                }
            }
            self.call_send_api(message_data)
        else:
            message_data = {
                "recipient": {
                    "id": sender_id
                },
                "message": {
                    "text": message_text
                }
            }
            self.call_send_api(message_data)
            if (menu_id):
                return_data = self.get_submenus_db(menu_id)
                for d in return_data:
                    self.send_text_message(sender_id, d[3], d[2], d[0])


    def call_send_api(self, data):
        r = requests.post(
            url="https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": settings.CONSTANTS['FB_TOKEN']},
            json=data
        )
        print(r.url)
        print(r.json())