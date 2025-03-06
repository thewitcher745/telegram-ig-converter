# Instagram Downloader Telegram Bot

A Telegram bot that automatically downloads Instagram posts and reels when links are shared in group chats or direct messages.

## Features

- Automatically detects Instagram links in messages
- Downloads both posts and reels from Instagram
- Works in both private chats and group conversations
- Sends the downloaded content directly in the chat
- Privacy-focused with minimal logging
- Cleans up temporary files after sending content

## Requirements

- Python 3.7+
- `python-telegram-bot` (v20.0+)
- `instaloader`

## Installation

1. Clone this repository:
```bash
git clone https://github.com/thewitcher745/telegram-ig-converter
cd instagram-telegram-bot
```

2. Install the required dependencies:
```bash
pip install python-telegram-bot instaloader
```

3. Create your Telegram bot:
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Follow the prompts to create a new bot
   - Copy your bot token

## Configuration

Set your Telegram bot token as a value of the key "BOT_TOKEN" in a file called `.env.secret` in the project root:

```bash
BOT_TOKEN="YOUR_BOT_TOKEN"
```

## Usage

1. Run the bot:
```bash
python bot.py
```

2. Add your bot to a group or start a direct conversation with it
3. Send an Instagram post or reel link
4. The bot will automatically download and send the content

## Bot Commands

- `/start` - Introduces the bot and explains its functionality
- `/help` - Shows usage instructions

## Privacy Considerations

This bot is designed with privacy in mind:
- Minimal logging without storing message content or personal data
- No persistent storage of downloaded content
- Files are deleted immediately after being sent
- No tracking or analytics

## Important Notes

1. Make sure your bot has the appropriate permissions:
   - In BotFather, set "Allow Groups" to enable group chat functionality
   - To read all messages in groups, disable Privacy Mode in BotFather settings

2. Be aware of Instagram's rate limits and Terms of Service:
   - Excessive usage may result in temporary IP blocking
   - This bot is intended for personal use only

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

[MIT License](LICENSE)

## Disclaimer

This bot is for educational purposes only. Use responsibly and in accordance with Instagram's Terms of Service. The developers of this bot are not responsible for any misuse or violations of Instagram's policies.