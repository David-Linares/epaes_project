"""
Django settings for epaesproject project.

Generated by 'django-admin startproject' using Django 1.11.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'pcw(j^=8&i8lkkce7r(cj@4vz#1l@+dc3@1tk062!)34(22h(-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Logger Config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters':{
        'detail':{
            'format': '%(levelname)s %(asctime)s [%(filename)s %(funcName)s %(lineno)d]: %(message)s'
        },
        'simple':{
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/epaes_%s.log' % datetime.datetime.now().strftime("%Y%m%d"),
            'formatter': 'detail'
        },
    },
    'loggers': {
        'webhook.views': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'webhook'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

ROOT_URLCONF = 'epaesproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'epaesproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'epaes_db',
        'USER': 'epaes_user',
        'PASSWORD': '6F857875ECE546BCB6A3405E6BEA38B3A4B94AA3',
        'HOST': 'localhost',
        'PORT': '3306',
        'CHARSET': 'utf8mb4',
        'COLLATE': 'utf8mb4_general_ci'
    }
}

CONSTANTS = {
    "CALCULATE_HISTORICAL": "select sum(extract(hour from timediff(date_finish_session, date_start_session))) as hours, sum(extract(minute from timediff(date_finish_session, date_start_session))) as minutes, sum(extract(second from timediff(date_finish_session, date_start_session))) as seconds  from session where id_user_session = '%s' group by id_user_session",
    "CREATE_SESSION": "insert into temp_session (id_user_session, date_finish_session) values ('%s', '%s')",
    "QUERY_CURRENT_SESSION": "select * from session where id_user_session = '%s' and date_start_session < '%s' and date_finish_session > '%s' and auto_ends_session <> 1 and user_ends_session <> 1",
    "UPDATE_SESSION": "update session set date_finish_session = '%s' where id_user_session = '%s' and auto_ends_session <> 1 and user_ends_session <> 1 ",
    "UPDATE_FINISH_SESSION": "update session set user_ends_session = 1 where id_user_session = '%s' and auto_ends_session <> 1 and user_ends_session <> 1 ",
    "QUERY_MESSAGES_FLOW": "select mch.* from messages as m inner join messages_relations as mr ON m.id_message = mr.message_parent inner join messages as mch on mr.message_child = mch.id_message where mr.message_parent = %d and mr.relation_status = 1",
    "QUERY_SPECIFIC_MESSAGE": "select id_message, description_message, id_type_message, message_response from messages where id_message = %d and is_message_button = 0 and message_status = 1",
    "QUERY_MESSAGES_BUTTON":"select mch.* from messages as m inner join messages_relations as mr ON m.id_message = mr.message_parent inner join messages as mch on mr.message_child = mch.id_message where mr.message_parent = %d and mch.is_message_button = 1 and mr.relation_status = 1",
    "QUERY_INIT_MESSAGES":"select id_message, description_message, id_type_message from messages where init_message = 1 and message_status = 1",
    "QUERY_MESSAGES_AUDIO_SITUATION": "select mch.* from messages as m inner join messages_relations as mr ON m.id_message = mr.message_parent inner join messages as mch on mr.message_child = mch.id_message where mr.message_parent = %d and mr.relation_status = 1 and mch.id_type_message = 3",
    "QUERY_MESSAGES_TEXT_AUDIO_SITUATION": "select mch.* from messages as m inner join messages_relations as mr ON m.id_message = mr.message_parent inner join messages as mch on mr.message_child = mch.id_message where mr.message_parent = %d and mr.relation_status = 1 and mch.id_type_message in (3,2)",
    "QUERY_MESSAGES_TEXT_SITUATION": "select mch.* from messages as m inner join messages_relations as mr ON m.id_message = mr.message_parent inner join messages as mch on mr.message_child = mch.id_message where mr.message_parent = %d and mr.relation_status = 1 and mch.id_type_message = 2",
    "UPDATE_CHAT_INFO": "insert into chat (id_session_chat, message_content, user_response) values (%d, '%s', %d);",
    "QUERY_INSERT_EVENT_LOGS": "insert into event_logs(facebook_event_id, type_event, user_id, facebook_timestamp) values ('%s', 1, '%s', %s);",
    "QUERY_INSERT_MESSAGES_LOGS": "insert into messages_logs ('message_id','value_message','sender_id','recipient_id','timestamp_message') values ('%s','%s','%s','%s','%s');",
    "QUERY_PARENT_MENU":"select m.* from messages as m inner join messages_relations as mr on m.id_message = mr.message_parent where mr.message_child in (select m.id_message from messages as m inner join messages_relations as mr on m.id_message = mr.message_parent where mr.message_child = %d) limit 1;",
    "HISTORICAL_MESSAGE": "En este tiempo has practicado el idioma en promedio %d horas, %d minutos y %d segundos.",
    "HISTORICAL_MESSAGE_SUCCESS": "Ánimo 👍, entre más tiempo practiques conmigo, más vas a mejorar en el idioma. 💪",
    "MESSAGE_NOT_FOUND": "Lo sentimos, en este momento no podemos atender tu solicitud. Estamos trabajando en ello. 👨‍🔧 👩‍🔧",
    "MESSAGE_CANT_GO_BACK": "Ya no hay más menús anteriores. ❎ Continúa con el actual.. ↪",
    "RESULT_AUDIO_WRONG": "Necesitas practicar más para mejorar tu español.. No te desanimes. Tu puntaje de este ejercicio fue de %d %%",
    "RESULT_AUDIO_NOT_WRONG": "Vas bien pero necesitas seguir practicando. Tu puntaje de este ejercicio fue de %d %%",
    "RESULT_AUDIO_MEDIUM": "Haz trabajado duro, se nota en tus resultados. Tu puntaje de este ejercicio fue de %d %%",
    "RESULT_AUDIO_OK": "Waooo Parece que hubieras nacido en Colombia!! Sorprendente!!. Tu puntaje de este ejercicio fue de %d %%",
    "RENEW_SESSION": "🚨 Tu sesión anterior ha caducado por tiempo de espera 🕘. Volveré a iniciarla para que sigas practicando... 🚨",
    "PATH_SAVE_AUDIOS": BASE_DIR + "/static/audios/facebook/audio_file_%s.mp4",
    "PATH_AUDIOS": BASE_DIR + "/static/audios/converted/audio_file_%s.flac",
    "PATH_AUDIOS_SITUATIONS": BASE_DIR + "/static/audios/situations/audio%s.flac",
    "PUBLIC_PATH_AUDIO": "/static/audios/situations/%s",
    # "PUBLIC_PATH_AUDIO": "/static/audios/facebook/audio_file_%s.mp4",
    "UNINTERPRETED_MESSAGE": "🤯 Lo siento, no logro entender lo que me quieres decir, voy a notificar a mis creadores para que me ayuden a entenderte en una próxima ocasión. 😣",
    "ANALYZE_AUDIO": "Estoy analizando tu respuesta, no te desesperes si tardo un poco. ⏱",
    "END_SESSION": "Terminamos trabajo por esta vez, espero verte pronto. 🤗",
    "MESSAGES_IMAGES": ["Que bonita imagen, es tuya? 😀", "Me gustan las imagenes, estoy aprendiendo a analizarlas. 🖼", "Intentas confundirme? 😕 No entiendo como puedo ayudarte a mejorar el idioma con esta imagen. Vamos a practicar... 🙂"],
    "NOT_WAIT_TEXT_YET": "No estaba esperando eso.. 🤔 Vamos a volver a iniciar la práctica y no le decimos a nadie.. 🤫",
    "NOT_WAIT_TEXT": "Me respondiste con algo que no esperaba. Intenta responder con un mensaje de voz repitiendo la oración. 🎙",
    "NOT_WAIT_AUDIO": "Me respondiste con algo que no esperaba. Intenta responder escribiendo lo que escuches en la grabación 🔊",
    "TRY_AGAIN": "Inténtalo nuevamente... 🤳",
    "NO_MORE_ATTEMPS": "Intentos disponibles: 0️⃣. Puedes intentar con otra categoría.",
    "TIME_SESSION": 600,
    "CONTINUE_MENU_ID": 3,
    "SITUATIONS_ARRAY": [12,13,14],
    "MENU_AUDIO_ID": 8,
    "MENU_TEXT_ID": 9,
    "TEXT_MENU_AUDIO_ID": 10,
    "FB_TOKEN": "EAAYy77b89Q8BAOvPUJZA5VRfOyX7x6SQCXdZBrb7MUM1Aue75ZAbpZBG2dwYAnuBdxqMxdj6DSM1QZASL3jhoZBIaRhwtHefl9HzOlxPeWjMIlVPEZCka9oYmVZCrwONGzEzNBJwwEf5sd5mWDC8jDZBvFd6xZAQ3KoXEXOgjTVZA2KpwZDZD",
    "VERIFY_TOKEN": "epaes_bot_ueb"
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = ''

STATICFILES_DIRS = [ os.path.join('static') ]

