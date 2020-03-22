import vk_api
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from os import getenv, environ
from dotenv import load_dotenv
import dialogflow_v2 as dialogflow
import logging
import telegram


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def set_vk_bot_logging(log_level, bot_token, chat_id):
    log_levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'error': logging.ERROR,
        'warning': logging.WARN,
    }
    tg_bot = telegram.Bot(token=bot_token)
    logger = logging.getLogger(__file__)
    logger.setLevel(log_levels[log_level])
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        )
    telegram_handler = TelegramLogsHandler(tg_bot, chat_id)
    telegram_handler.setFormatter(formatter)
    logger.addHandler(telegram_handler)
    return logger


def invoke_dialog_flow(text):
    session_client = dialogflow.SessionsClient()
    session_id = 'devman_dialog_flow'
    session = session_client.session_path(dialogflow_project_id, session_id)
    text_input = dialogflow.types.TextInput(
        text=text,
        language_code='ru_RUS',
        )
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(
        session=session,
        query_input=query_input,
        )
    if response.query_result.intent.is_fallback:
        return
    return response.query_result.fulfillment_text


def text_message(vk_session, vk):
    while True:
        try:
            longpoll = VkLongPoll(vk_session)
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    dialogflow_response = invoke_dialog_flow(event.text)
                    if not dialogflow_response:
                        continue
                    vk.messages.send(
                        user_id=event.user_id,
                        message=dialogflow_response,
                        random_id=random.randint(1, 1000),
                        )
        except Exception as error:
            logger.error(error, exc_info=True)


if __name__ == '__main__':
    load_dotenv()
    vk_token = getenv('VK_TOKEN')
    google_credentials_file = getenv('GOOGLE_CRED')
    if google_credentials_file:
        environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials_file
    dialogflow_project_id = getenv('DIALOG_FLOW_ID')
    telebot_token = getenv('TELEGRAM_BOT_TOKEN')
    logger_chat_id = getenv('LOGGER_CHAT_ID')
    logger = set_vk_bot_logging('info', telebot_token, logger_chat_id)
    logger.info('Bot {0} has started!'.format(__file__))
    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    text_message(vk_session, vk)
