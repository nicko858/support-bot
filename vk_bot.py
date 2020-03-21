import vk_api
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from os import getenv, environ
from dotenv import load_dotenv
import dialogflow_v2 as dialogflow


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


if __name__ == '__main__':
    load_dotenv()
    vk_token = getenv('VK_TOKEN')
    environ['GOOGLE_APPLICATION_CREDENTIALS'] = getenv('GOOGLE_CRED')
    dialogflow_project_id = getenv('DIALOG_FLOW_ID')
    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    text_message(vk_session, vk)
