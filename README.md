# telegram-file-sender

Docker image for sending files via Telegram Bot API.

## Example usage

```shell
docker run --rm \
  -w [path_to_dir_with_your_file] \
  -v [path_to_dir_with_your_file]:[path_to_dir_with_your_file]:ro \
  -e TELEGRAM_BOT_TOKEN="BotAccessToken" \
  -e TELEGRAM_CHAT_ID="ChatId" \
  -e TELEGRAM_CHAT_MESSAGE="VerboseFileDescription" \
  -e TELEGRAM_FILE_NAME="FullPathToYourFile" \
  ghcr.io/dmitriysafronov/telegram-file-sender:latest
```
