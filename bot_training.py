from os import getenv, environ
from os import access
from os import path
from os import R_OK
import json
from google.api_core import exceptions

import dialogflow_v2 as dialogflow

from dotenv import load_dotenv

from argparse import ArgumentTypeError
import argparse


def check_file_path(file_path):
    read_ok = access(path.dirname(file_path), R_OK)
    error_msg = "Access error or directory {0} doesn't exist!"
    if not read_ok:
        raise ArgumentTypeError(error_msg.format(file_path))
    elif path.isdir(file_path):
        raise ArgumentTypeError("The '{0}' is not a file!".format(file_path))
    return file_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('intent_file', type=check_file_path)
    return parser.parse_args()


def load_json(intent_file):
    with open(intent_file, 'r') as file_handler:
        file_content = file_handler.read()
    return json.loads(file_content)


def train_agent(dialogflow_project_id):
    client = dialogflow.AgentsClient()
    parent = client.project_path(str(dialogflow_project_id))
    client.train_agent(parent)


def parse_raw_intents_for_dialog_flow(raw_intents):
    parsed_intents = []
    for intent_name, intent_params in raw_intents.items():
        training_phrases = []
        for question in intent_params['questions']:
            training_phrases.append({'parts': [{'text': question}]})
        intent = {
            'display_name': intent_name,
            'messages': [{'text': {'text': [intent_params['answer']]}}],
            'training_phrases': training_phrases,
        }
        parsed_intents.append(intent)
    return parsed_intents


def create_intent(intent, dialogflow_project_id):
    client = dialogflow.IntentsClient()
    parent = client.project_agent_path(str(dialogflow_project_id))
    client.create_intent(parent, intent)


if __name__ == '__main__':
    load_dotenv()
    environ['GOOGLE_APPLICATION_CREDENTIALS'] = getenv('GOOGLE_CRED')
    dialogflow_project_id = getenv('DIALOG_FLOW_ID')
    cli_args = parse_args()
    intent_file = cli_args.intent_file
    raw_intents = load_json(intent_file)
    parsed_intents = parse_raw_intents_for_dialog_flow(
        raw_intents,
        )
    for intent in parsed_intents:
        try:
            create_intent(intent, dialogflow_project_id)
            train_agent(dialogflow_project_id)
        except exceptions.BadRequest as error:
            print('Exception occured during training bot procedure:\n{0}'.format(
                error,
                ),
                  )
    print('Training bot procedure completed!')
