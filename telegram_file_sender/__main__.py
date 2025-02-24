#!/usr/bin/env python3

from os import environ
import requests


def get_env_var(variable_name):
    result = environ.get(variable_name)
    if result is None or result == "":
        raise Exception(f"The environment variable [{variable_name}] is required!")
    return result


def main():
    TELEGRAM_BOT_TOKEN = get_env_var("TELEGRAM_BOT_TOKEN")
    TELEGRAM_FILE_NAME = get_env_var("TELEGRAM_FILE_NAME")
    TELEGRAM_CHAT_ID = int(get_env_var("TELEGRAM_CHAT_ID"))
    TELEGRAM_CHAT_MESSAGE = get_env_var("TELEGRAM_CHAT_MESSAGE")

    try:
        response = requests.post(f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument', data={'chat_id': TELEGRAM_CHAT_ID, 'parse_mode': "MarkdownV2", 'caption': TELEGRAM_CHAT_MESSAGE}, files=open(TELEGRAM_FILE_NAME,'rb'), stream=True)
        print(response.text)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
