# Spam Stopper Bot

A powerful and customizable Python-based IRC bot for spam detection, NickServ authentication, and moderation.

## Features

- Automatic NickServ and Operserv authentication.
- Spam detection using customizable regex patterns.
- Handles spam in both public and private messages.
- Supports multiple akill types, including custom commands.
- Robust logging for monitoring and debugging.
- Graceful reconnection handling.
- Easy-to-configure settings for server, credentials, and behavior.

## Installation

To use Spam Stopper Bot, follow these steps:

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/SpamStopperBot.git
Navigate to the project directory:
bash
Copy code
cd SpamStopperBot
Install the required dependencies:
bash
Copy code
pip install irc jaraco.stream
Configure the bot by editing the SpamStopperBot.py file with your IRC server and authentication details.
Run the bot:
bash
Copy code
python SpamStopperBot.py
Configuration
All configuration variables are located at the top of the SpamStopperBot.py file. Below are some key settings:

IRC Server: Set the IRC server, port, and channel.
NickServ: Configure your NickServ nickname and password for authentication.
Operserv: Configure your Operserv login and password for issuing akill commands.
Spam Keywords: Add or modify spam detection regex patterns.
Akill Configuration: Enable/disable akill and customize command formats.
Example configuration:


IRC_SERVER = "irc.example.com"
IRC_PORT = 6697
CHANNEL = "#example-channel"
BOT_NICKNAME = "SpamStopperBot"
NICKSERV_PASSWORD = "your_password"
OPERSERV_LOGIN = "your_operserv_login"
OPERSERV_PASSWORD = "your_operserv_password"
Usage
Once the bot is running, it will:

Authenticate with NickServ to identify its nickname.
Authenticate with Operserv (if credentials are provided).
Monitor messages in the configured channel and private messages for spam.
Take appropriate action (e.g., akill) if spam is detected.
Spam patterns and actions are fully customizable through the configuration section.

Help and Support
If you need help or want to learn more about the bot, join us on irc.twistednet.org:

Channel: #dev
Channel: #twisted
We'd love to hear from you!

Credits
The Spam Stopper Bot was created by gh0st.

Created with ❤️ by gh0st. Licensed under MIT.


 



