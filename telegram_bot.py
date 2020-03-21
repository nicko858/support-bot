from os import getenv, environ

from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

import logging
import dialogflow_v2 as dialogflow


def set_insta_bot_logging(log_level):
    log_levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'error': logging.ERROR,
        'warning': logging.WARN,
    }
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=log_levels[log_level],
        )


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


def text_message(bot, update):
    dialogflow_response = invoke_dialog_flow(update.message.text)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=dialogflow_response,
        )


if __name__ == '__main__':
    load_dotenv()
    telebot_token = getenv('TELEGRAM_BOT_TOKEN')
    environ['GOOGLE_APPLICATION_CREDENTIALS'] = getenv('GOOGLE_CRED')
    dialogflow_project_id = getenv('DIALOG_FLOW_ID')
    set_insta_bot_logging('info')
    updater = Updater(token=telebot_token)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    text_msg_handler = MessageHandler(Filters.text, text_message)
    dispatcher.add_handler(text_msg_handler)
    dispatcher.add_handler(start_handler)
    updater.start_polling()
