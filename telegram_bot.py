from os import getenv, environ

from dotenv import load_dotenv
import telegram
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import logging
import dialogflow_v2 as dialogflow


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def set_insta_bot_logging(log_level, bot_token, chat_id):
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


def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Здравствуйте!',
        )


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
    return response.query_result.fulfillment_text


def handle_text_message(bot, update):
    try:
        dialogflow_response = invoke_dialog_flow(update.message.text)
        bot.send_message(
            chat_id=update.message.chat_id,
            text=dialogflow_response,
            )
    except Exception as error:
        logger.error(error, exc_info=True)


if __name__ == '__main__':
    load_dotenv()
    telebot_token = getenv('TELEGRAM_BOT_TOKEN')
    logger_chat_id = getenv('LOGGER_CHAT_ID')
    google_credentials_file = getenv('GOOGLE_CRED')
    if google_credentials_file:
        environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials_file
    dialogflow_project_id = getenv('DIALOG_FLOW_ID')
    updater = Updater(token=telebot_token)
    logger = set_insta_bot_logging('info', telebot_token, logger_chat_id)
    logger.info('Bot {0} has started!'.format(__file__))
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    text_msg_handler = MessageHandler(Filters.text, handle_text_message)
    dispatcher.add_handler(text_msg_handler)
    dispatcher.add_handler(start_handler)
    updater.start_polling()
