# -*- coding: utf-8 -*-
import glob
import json
import logging
import datetime
import subprocess
import urllib
from random import randint

import os
import speech_recognition as sr
import redis
import requests
from django.db import connection
from fuzzywuzzy import fuzz
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings


rdb = redis.StrictRedis(host='localhost', port=6379)
logger = logging.getLogger(__name__)
tunnel = "https://chatbotepaes.ngrok.io"


class WebhookResponse(APIView):

    def get(self, request):
        mode = request.query_params.get("hub.mode", False)
        challenge = request.query_params.get("hub.challenge", False)
        verify_token = request.query_params.get("hub.verify_token", False)
        if mode == 'subscribe' and verify_token == settings.CONSTANTS['VERIFY_TOKEN']:
            logger.info("Validate token verify")
            return Response(json.loads(challenge), status=200)
        else:
            logger.error("Please Validate the token")
            return Response(status=403)

    # Recibe cualquier petición de FB
    def post(self, request):
        data = request.data
        logger.info("Llega petición")
        logger.debug(data)
        if data['object'] == 'page':
            entry = data['entry']
            logger.info("Llega Page")
            logger.info("Entradas: "+str(len(entry)))
            for i in entry:
                # query = settings.CONSTANTS['QUERY_INSERT_EVENT_LOGS'] % (i['id'], i['messaging'][0]['sender']['id'],
                # i['messaging'][0]['timestamp'])
                # save_info_messages_events(i['messaging'][0]['sender']['id'], query)
                messaging = i['messaging']
                for j in messaging:  # Evalúa los datos que llegan de la petición de FB
                    info_session = check_session(j['sender']['id'])
                    if info_session == -100 and j['postback']['payload'] != "start":
                        save_chat(j['sender']['id'], "start", user_response=True)
                        logger.debug("Renueva sesión")
                        send_text_message(j['sender']['id'], settings.CONSTANTS['RENEW_SESSION'], 2)
                        classify_postback(j['sender']['id'], "start")
                    else:
                        rdb.hset(j['sender']['id'], "last_request", j['timestamp'])
                        if "message" in j:  # Si escriben un mensaje
                            logger.debug("Llega mensaje")
                            classify_message(j['sender']['id'], j['message'])
                            # save_chat(j['sender']['id'], j['message']['text'], user_response=True)
                            # query = settings.CONSTANTS['QUERY_INSERT_MESSAGES_LOGS'] %
                            # (j['message']['mid'], j['message']['text'], j['sender']['id'],
                            # j['recipient']['id'], j['timestamp'])
                            # save_info_messages_events(j['sender']['id'], query)
                        elif "postback" in j:  # Si oprimen un botón
                            save_chat(j['sender']['id'], j['postback']['payload'], user_response=True)
                            logger.debug("Llega Postback")
                            classify_postback(j['sender']['id'], j['postback']['payload'])
                            # get_menus_db(j['postback']['payload'], j['sender']['id'])
        else:
            pass
        logger.info("Devuelve 200 OK")
        return Response(status=200)


# Util Methods
def get_file_audio(path, file_name):
    logger.debug(path)
    lstdir = os.walk(path)
    lstfiles = []
    for root, dirs, files in lstdir:
        for file in files:
            (nameFile, extension) = os.path.splitext(file)
            if nameFile.startswith(file_name):
                lstfiles.append(nameFile + extension)
    return lstfiles[randint(0, len(lstfiles))]


def get_buttons_format(data_buttons):
    array_buttons = []
    for db in data_buttons:
        array_buttons.append({
            "type": "postback",
            "title": db[1],
            "payload": db[0],
        })
    return array_buttons


def verify_response(sender_id):
    accepted = rdb.hget(sender_id, "selection_type_practice") or "0"
    logger.info("Verificando Mensaje")
    logger.info(accepted)
    if int(accepted) == settings.CONSTANTS['MENU_AUDIO_ID']:  # Audio
        return "audio"
    elif int(accepted) == settings.CONSTANTS['TEXT_MENU_AUDIO_ID']:
        return "text"
    else:
        return "text"


def reset_fields_db(sender_id, all=False):
    if all:
        rdb.hdel(sender_id, "url_audio", "situation", "attemps_num", "pending_message", "rpta_audio", "audio_test")
        rdb.hdel(sender_id, "last_menu_id")
        rdb.hdel(sender_id, "last_menu_options_id")
    else:
        rdb.hdel(sender_id, "url_audio", "situation", "attemps_num", "pending_message", "rpta_audio", "audio_test")



def similar(a, b):
    logger.debug("Primero: "+ a)
    logger.debug("Segundo: " + b)
    return fuzz.token_set_ratio(a, b)


def get_audio(sender_id, payload):
    url = payload['url']
    download_time = sender_id + "_" + str(datetime.datetime.now().timestamp())
    urllib.request.urlretrieve(url, settings.CONSTANTS['PATH_SAVE_AUDIOS'] % download_time)
    rdb.hset(sender_id, "url_audio", download_time)
    return download_time


def classify_postback(sender_id, postback):
    logger.info("Clasificando Postback")
    logger.info(postback)
    if postback == "start":  # Cuando oprime el botón de inicio
        reset_fields_db(sender_id, all=True)
        get_init_message_db(sender_id, init_message=True)
    else:
        if 8 <= int(postback) <= 10:
            save_user_selection(sender_id, postback)
            get_init_message_db(sender_id, postback)
        elif int(postback) == 5:
            calculate_historical(sender_id)
            get_init_message_db(sender_id, postback, menu_id=settings.CONSTANTS['CONTINUE_MENU_ID'])
        elif int(postback) == 6:
            get_init_message_db(sender_id, postback)
            get_init_message_db(sender_id, postback, menu_id=settings.CONSTANTS['CONTINUE_MENU_ID'])
        elif int(postback) == -500:  # Regresar al menú anterior
            logger.info("Volver al menú anterior")
            logger.info(int(rdb.hget(sender_id, "last_menu_options_id")))
            get_init_message_db(sender_id, int(rdb.hget(sender_id, "last_menu_options_id") or 0), go_back=True)
        elif int(postback) == -1000:  # Regresar al menú anterior
            logger.info("Terminar Sesión")
            end_session(sender_id)
            send_text_message(sender_id, settings.CONSTANTS['END_SESSION'], 2)
        elif int(postback) in settings.CONSTANTS['SITUATIONS_ARRAY']:
            # get_init_message_db(sender_id, postback)
            logger.debug("Situación...")
            rdb.hset(sender_id, "situation", int(postback))
            get_init_message_db(sender_id, postback, situation=True)
        else:
            get_init_message_db(sender_id, postback)


def classify_message(sender_id, message):
    logger.info("Clasificando Mensaje")
    logger.info(message)
    if 'text' in message:  # Llega mensaje de Texto
        if verify_response(sender_id) == "text":
            logger.info("Texto")
            compare_audios(sender_id, message['text'])
        else:
            send_text_message(sender_id, settings.CONSTANTS['NOT_WAIT_TEXT'], 2)
    elif 'attachments' in message:
        for attach in message['attachments']:
            if attach['type'] == "audio":
                if verify_response(sender_id) == "audio":
                    logger.info("Audio")
                    logger.info(attach)
                    send_text_message(sender_id, settings.CONSTANTS['ANALYZE_AUDIO'], 2)
                    process_audio(sender_id, attach['payload'])
                else:
                    send_text_message(sender_id, settings.CONSTANTS['NO_WAIT_AUDIO'], 2)
            elif attach['type'] == "image":
                send_text_message(sender_id, settings.CONSTANTS['MESSAGES_IMAGES'][randint(0, len(settings.CONSTANTS['MESSAGES_IMAGES']))], 2)
            elif attach['type'] == "location":
                if verify_response(sender_id) == attach['type']:
                    logger.info("Ubicación")
                else:
                    send_text_message(sender_id, settings.CONSTANTS['UNINTERPRETED_MESSAGE'], 2)
            else:
                logger.info("Otro Adjunto")
                logger.info(attach['type'])
                send_text_message(sender_id, settings.CONSTANTS['UNINTERPRETED_MESSAGE'], 2)
    else:
        logger.info("otro Mensaje")
        logger.info(message)
        send_text_message(sender_id, settings.CONSTANTS['UNINTERPRETED_MESSAGE'], 2)


def try_again(sender_id):
    attemps_num = int(rdb.hget(sender_id, "attemps_num") or 3)
    if attemps_num > 0:
        rdb.hset(sender_id, "attemps_num", attemps_num - 1)
        send_text_message(sender_id, settings.CONSTANTS['TRY_AGAIN'], 2)
        last_menu_id = rdb.hget(sender_id, "last_menu_id")
        send_audio = str(rdb.hget(sender_id, "audio_test"), "utf-8")
        send_text_message(sender_id, send_audio, 3)
    else:
        send_text_message(sender_id, settings.CONSTANTS['NO_MORE_ATTEMPS'], 2)
        get_init_message_db(sender_id, menu_id=rdb.hget(sender_id, "last_menu_options_id"))

# DB Connection Methods
def get_init_message_db(sender_id, menu_parent=None, init_message=False, menu_id=None, situation=False,
                        go_back=False):
    logger.info("Consultando mensajes")
    logger.info("Mensajes Iniciales")
    logger.info(menu_parent)
    logger.info(menu_id)
    logger.info(init_message)
    logger.info(situation)
    query = None
    send_audio = None
    if menu_id and not go_back:
        query = settings.CONSTANTS['QUERY_SPECIFIC_MESSAGE'] % int(menu_id)
    elif go_back:
        query = settings.CONSTANTS['QUERY_PARENT_MENU'] % int(menu_parent)
    elif situation:
        logger.info("Situation...")
        logger.info(int(rdb.hget(sender_id, "selection_type_practice")))
        rdb.hset(sender_id, "attemps_num", 3)
        if int(rdb.hget(sender_id, "selection_type_practice")) == settings.CONSTANTS['MENU_AUDIO_ID']:
            rdb.hset(sender_id, "pending_message", settings.CONSTANTS['MENU_AUDIO_ID'])
        elif int(rdb.hget(sender_id, "selection_type_practice")) == settings.CONSTANTS['TEXT_MENU_AUDIO_ID']:
            rdb.hset(sender_id, "pending_message", settings.CONSTANTS['MENU_TEXT_ID'])
        if int(menu_parent) == 12:
            prefix = "ci"
        elif int(menu_parent) == 13:
            prefix = "r"
        else:
            prefix = "c"
        send_audio = settings.CONSTANTS['PUBLIC_PATH_AUDIO'] % \
                     get_file_audio(settings.BASE_DIR + "/static/audios/situations/", "audio"+prefix)
    elif not init_message:
        query = settings.CONSTANTS['QUERY_MESSAGES_FLOW'] % int(menu_parent)
    else:
        query = settings.CONSTANTS['QUERY_INIT_MESSAGES']
    try:
        if not situation:
            data = query_fnt(query)
            if len(data) > 0:
                # if situation:
                #     get_submessages_button_db(sender_id, data[])
                for d in data:
                    get_submessages_button_db(sender_id, d)
            else:
                if go_back:
                    send_text_message(sender_id, settings.CONSTANTS['MESSAGE_CANT_GO_BACK'], 2)
                else:
                    send_text_message(sender_id, settings.CONSTANTS['MESSAGE_NOT_FOUND'], 2)
                get_init_message_db(sender_id, menu_id=rdb.hget(sender_id, "last_menu_options_id"))
        else:
            logger.info("Enviando audio...")
            logger.info(send_audio)
            logger.debug("%s%s" % (settings.BASE_DIR, send_audio))
            res = convert_audio("%s%s" % (settings.BASE_DIR, send_audio))
            logger.info("Texto Audio Enviado...")
            logger.info(res)
            rdb.hset(sender_id, "rpta_audio", str(res))
            rdb.hset(sender_id, "audio_test", send_audio)
            send_text_message(sender_id, send_audio, 3)
    except Exception as e:
        logger.error("Se produjo un error..")
        logger.error(e)


def get_submessages_button_db(sender_id, data_menu):
    rdb.hset(sender_id, "last_menu_id", data_menu[0])
    logger.info("Consulta submenus para opciones")
    logger.info(data_menu)
    try:
        query = settings.CONSTANTS['QUERY_MESSAGES_BUTTON'] % int(data_menu[0])
        data = query_fnt(query)
        if len(data) > 0:  # Tiene botones y arma estructura.
            rdb.hset(sender_id, "last_menu_options_id", data_menu[0])
            logger.info("Si hay submenus, se procede a crear estructura de botones...")
            # send_text_message(sender_id, data_menu[1], data_menu[2], data_menu[0], buttons=data,
            #                                 structure=True)
            send_text_message(sender_id, data_menu[1], data_menu[2], buttons=data, structure=True)
        else:
            logger.info("No hay submenus, se envía el mensaje.")
            send_text_message(sender_id, data_menu[1], data_menu[2], data_menu[0])
            # Manda el mensaje Plano
    except Exception as e:
        logger.error("Se produjo un error..")
        logger.error(e)


def save_user_selection(sender_id, data_save):
    logger.info("Guardando Info del chat del usuario...")
    logger.info(data_save)
    try:
        rdb.hset(sender_id, "selection_type_practice", data_save)
    except Exception as e:
        logger.error("Se produjo un error..")
        logger.error(e)


def save_chat(sender_id, message_content, user_response=False):
    logger.info("Agregando información al chat...")
    logger.info(message_content)
    try:
        info_session = check_session(sender_id)
        logger.info(info_session)
        logger.info(message_content)
        logger.info(user_response)
        query = settings.CONSTANTS['UPDATE_CHAT_INFO'] % (info_session, message_content, user_response)
        with connection.cursor() as cursor:
            cursor.execute(query)
    except Exception as e:
        logger.error("Se produjo un error..")
        logger.error(e)


def query_fnt(query):
    logger.info("Ejecuta consulta...")
    logger.info(query)
    with connection.cursor() as cursor:
        cursor.execute("SET NAMES utf8mb4;")
        cursor.execute("SET SQL_SAFE_UPDATES = 0;")
        cursor.execute(query)
        data = cursor.fetchall()
        logger.info(data)
        return data


# Session Methods
def check_session(sender_id):
    logger.info("Consultando Sesión...")
    logger.info(sender_id)
    try:
        tsn = datetime.datetime.now()
        query = settings.CONSTANTS['QUERY_CURRENT_SESSION'] % (sender_id, tsn, tsn)
        logger.debug(query)
        with connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            if len(data) == 0:  # No hay una sesión vigente del usuario
                logger.info("No existía una sesión del usuario, configurando la sesión...")
                rdb.sadd("current_sessions", sender_id)  # Agrega el id a las sesiones existentes.
                rdb.expire(sender_id, settings.CONSTANTS['TIME_SESSION'])
                tsn = datetime.datetime.now()
                tsv = tsn + datetime.timedelta(seconds=settings.CONSTANTS['TIME_SESSION'])
                query = settings.CONSTANTS['CREATE_SESSION'] % (sender_id, tsv)
                logger.debug(query)
                cursor.execute(query)
                data = cursor.fetchall()
                logger.info(data)
                return -100
            else:
                if rdb.exists(sender_id):
                    logger.info("Actualizando tiempo de vencimiento de sesión")
                    rdb.expire(sender_id, settings.CONSTANTS['TIME_SESSION'])
                    tsn = datetime.datetime.now()
                    tsv = tsn + datetime.timedelta(seconds=settings.CONSTANTS['TIME_SESSION'])
                    query = settings.CONSTANTS['UPDATE_SESSION'] % (tsv, sender_id)
                    logger.debug(query)
                    cursor.execute(query)
                    data = cursor.fetchall()
                    logger.info(data)
                    return 200
                else:
                    logger.info("Sesión iniciada en BD pero no en redis, configurando la sesión")
                    rdb.sadd("current_sessions", sender_id)  # Agrega el id a las sesiones existentes.
                    # Agrega un  tiempo de expiración en la sesion
                    rdb.expire(sender_id, settings.CONSTANTS['TIME_SESSION'])
                return data[0][0]
    except Exception as e:
        logger.error("Se produjo un error..")
        logger.error(e)


def end_session(sender_id):
    query = settings.CONSTANTS['UPDATE_FINISH_SESSION'] % sender_id
    query_fnt(query)
    return 200


def save_info_messages_events(query):
    logger.info("Guardando mensaje o evento")
    try:
        query_fnt(query)
        return True
    except Exception as e:
        logger.error("Se produjo un error..")
        logger.error(str(e).index("Duplicate"))
        if str(e).index("Duplicate") != -1:
            logger.error("Registro Duplicado, no se guardará en la base de datos!")
        return False


# Historical Methods
def calculate_historical(sender_id):
    logger.info("Calculando información de uso del aplicativo...")
    try:
        query = settings.CONSTANTS['CALCULATE_HISTORICAL'] % sender_id
        result = query_fnt(query)
        seconds = int(60 * (abs(result[0][2] / 60) - int(result[0][2] / 60))) if int(result[0][2] / 60) > 0 \
            else result[0][2]
        minutes = int(result[0][2] / 60)
        minutes += int(60 * (abs(result[0][1] / 60) - int(result[0][1] / 60))) if int(result[0][1] / 60) > 0 \
            else result[0][1]
        minutes -= 10
        hours = int(result[0][1] / 60)
        hours += result[0][0]
        logger.info("hours " + str(hours))
        logger.info("minutes " + str(minutes))
        logger.info("seconds " + str(seconds))
        send_text_message(sender_id, settings.CONSTANTS['HISTORICAL_MESSAGE'] % (hours, minutes, seconds), 2)
        send_text_message(sender_id, settings.CONSTANTS['HISTORICAL_MESSAGE_SUCCESS'], 2)
    except Exception as e:
        logger.error("Se produjo un error..")
        logger.error(e)


# Api Connection Methods
def send_text_message(sender_id, message_content, type_content, buttons=None, structure=False,
                      messaging_type=None):
    logger.info("Tipo de Contenido")
    logger.info(type_content)
    if structure:
        if buttons:
            buttons = get_buttons_format(buttons)
            message_data = {
                "recipient": {
                    "id": sender_id
                },
                "message": {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "button",
                            "text": message_content,
                            "buttons": buttons
                        }
                    }
                }
            }
            if messaging_type:
                message_data['messaging_type'] = messaging_type
            call_send_api(message_data)
        else:
            logger.error("Hace falta los datos de los botones para armar la estructura.")
            # Cambiar Log de Error
    elif type_content == 2:  # Text
        message_data = {
            "recipient": {
                "id": sender_id
            },
            "message": {
                "text": message_content
            }
        }
        if messaging_type:
            message_data['messaging_type'] = messaging_type
        call_send_api(message_data)
    elif type_content == 4:  # Image
        message_data = {
            "recipient": {
                "id": sender_id
            },
            "message": {
                "attachment": {
                    "type": "image",
                    "payload": {
                        "url": message_content,
                        "is_reusable": True
                    }
                }
            }
        }
        if messaging_type:
            message_data['messaging_type'] = messaging_type
        call_send_api(message_data)
    elif type_content == 3:  # Audio
        message_data = {
            "recipient": {
                "id": sender_id
            },
            "message": {
                "attachment": {
                    "type": "audio",
                    "payload": {
                        "url": "%s/%s" % (tunnel, message_content)
                    }
                }
            }
        }
        if messaging_type:
            message_data['messaging_type'] = messaging_type
        call_send_api(message_data)


def call_send_api(data):
    requests.post(
        url="https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": settings.CONSTANTS['FB_TOKEN']},
        json=data
    )


# Audio Manager Methods
def process_audio(sender_id, attach):
    name_audio = get_audio(sender_id, attach)
    logger.info(name_audio)
    command = "ffmpeg -i %s -ab 160k -ac 2 -ar 44100 -vn %s" % (settings.CONSTANTS['PATH_SAVE_AUDIOS'] % name_audio,
                                                                settings.CONSTANTS['PATH_AUDIOS'] % name_audio)
    subprocess.call(command, shell=True)
    res = convert_audio(settings.CONSTANTS['PATH_AUDIOS'] % name_audio)  # Analiza la respuesta del usuario
    compare_audios(sender_id, res)


def process_local_audio(path):
    command = "ffmpeg -i %s -ab 160k -ac 2 -ar 44100 -vn %s" % (path,
                                                                path)
    subprocess.call(command, shell=True)
    res = convert_audio(path)
    return res


def convert_audio(url):
    try:
        logger.debug(url)
        r = sr.Recognizer()
        harvard = sr.AudioFile(url)
        with harvard as source:
            audio = r.record(source)
        res = r.recognize_google(audio, language="es-CO")
    except Exception as e:
        logger.error("Se presentó un error en la conversión del audio.")
        logger.error(e)
        res = ""
    return res


def compare_audios(sender_id, res):
    # logger.info(rdb.hget(sender_id, "last_menu_id"))
    # query = settings.CONSTANTS['QUERY_SPECIFIC_MESSAGE'] % int(rdb.hget(sender_id, "last_menu_id"))
    # data = query_fnt(query)[0]
    # response = data[3]
    try:
        response = str(rdb.hget(sender_id, "rpta_audio"), "utf-8")
        send_text_message(sender_id, settings.CONSTANTS['ANALYZE_AUDIO'], 2)
        percent = similar(response, res)
        if 0 <= percent <= 40:
            send_text_message(sender_id, settings.CONSTANTS['RESULT_AUDIO_WRONG'] % percent, 2)
            try_again(sender_id)
        elif 40 < percent <= 55:
            send_text_message(sender_id, settings.CONSTANTS['RESULT_AUDIO_NOT_WRONG'] % percent, 2)
            try_again(sender_id)
        elif 55 < percent <= 75:
            send_text_message(sender_id, settings.CONSTANTS['RESULT_AUDIO_MEDIUM'] % percent, 2)
            try_again(sender_id)
        elif 75 < percent:
            send_text_message(sender_id, settings.CONSTANTS['RESULT_AUDIO_OK'] % percent, 2)
            get_init_message_db(sender_id, menu_id=rdb.hget(sender_id, "last_menu_options_id"))
    except Exception as e:
        send_text_message(sender_id, settings.CONSTANTS['NOT_WAIT_TEXT_YET'], 2)
        get_init_message_db(sender_id, menu_id=rdb.hget(sender_id, "last_menu_options_id"))
        logger.error("Se ha producido un error..")
        logger.error(e)
