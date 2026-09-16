import logging
import sys
from os import environ

import requests

logger = logging.getLogger(__name__)


def get_env_var(variable_name: str) -> str:
    result = environ.get(variable_name)
    if result is None or result == "":
        raise ValueError(f"The environment variable [{variable_name}] is required!")
    return result


def main() -> int:
    """Send a document via the Telegram Bot API.

    Returns a process exit code: 0 on success, 1 on any failure.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        TELEGRAM_BOT_TOKEN = get_env_var("TELEGRAM_BOT_TOKEN")
        TELEGRAM_FILE_NAME = get_env_var("TELEGRAM_FILE_NAME")
        TELEGRAM_CHAT_ID = int(get_env_var("TELEGRAM_CHAT_ID"))
        TELEGRAM_CHAT_MESSAGE = get_env_var("TELEGRAM_CHAT_MESSAGE")
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    # Mask token for safe logging (hide credential from logs)
    masked_token = "*" * len(TELEGRAM_BOT_TOKEN)

    try:
        with open(TELEGRAM_FILE_NAME, "rb") as document:
            logger.info("Sending document to chat %s", TELEGRAM_CHAT_ID)
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
                data={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": TELEGRAM_CHAT_MESSAGE,
                },
                files={"document": document},
                timeout=60.0,
            )
            # raise_for_status() turns Telegram API errors (HTTP 400/404/...)
            # into exceptions, so a failed send never looks like a success.
            response.raise_for_status()
            logger.info("Document sent successfully to chat %s", TELEGRAM_CHAT_ID)
    except (OSError, requests.RequestException) as exc:
        # Any failure must result in a non-zero exit code, otherwise the
        # container/CI run would report success although the file was not sent.
        # OSError covers open() failures, RequestException covers API failures.
        # Mask the token in error logs to avoid leaking credentials.
        masked_exc = str(exc).replace(TELEGRAM_BOT_TOKEN, masked_token)
        logger.error("Failed to send document: %s", masked_exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
