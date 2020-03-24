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


def init_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('intent_file', type=check_file_path)
    return parser.parse_args()


def load_json(intent_file):
    with open(intent_file, 'r') as file_handler:
        file_content = file_handler.read()
    return json.loads(file_content)


def train_agent(dialogflow_project_id):
    client = dialogflow.AgentsClient()
    parent = client.project_path('{0}'.format(dialogflow_project_id))
    try:
        client.train_agent(parent)
    except exceptions.BadRequest as error:
        print(error)


def parse_json_for_dialog_flow_intent(raw_intent_json):
    parsed_intents_list = []
    for intent_name, intent_params in raw_intent_json.items():
        intent = {}
        intent['display_name'] = intent_name
        intent['messages'] = [{'text': {'text': [intent_params['answer']]}}]
        intent['training_phrases'] = [
            {'parts': [{'text': question}]} for
            question in intent_params['questions']
            ]
        parsed_intents_list.append(intent)
    return parsed_intents_list


def create_intent(intent_list, dialogflow_project_id):
    client = dialogflow.IntentsClient()
    parent = client.project_agent_path('{0}'.format(dialogflow_project_id))
    for intent in intent_list:
        try:
            client.create_intent(parent, intent)
        except exceptions.BadRequest as error:
            print(error)


if __name__ == '__main__':
    load_dotenv()
    environ['GOOGLE_APPLICATION_CREDENTIALS'] = getenv('GOOGLE_CRED')
    dialogflow_project_id = getenv('DIALOG_FLOW_ID')
    cli_args = init_arg_parser()
    intent_file = cli_args.intent_file
    raw_intent_json = load_json(intent_file)
    intent_list = parse_json_for_dialog_flow_intent(
        raw_intent_json,
        )
    create_intent(intent_list, dialogflow_project_id)
    train_agent(dialogflow_project_id)
    print('Training bot procedure completed!')
