
# IRC SpamStopper

**For support and help, or just to visit, come to** [irc.twistednet.org](irc://irc.twistednet.org) **channels #dev and #twisted**  
**SpamBot made by gh0st**  

![GhostBot Logo](https://raw.githubusercontent.com/gh0st68/web/main/TwistedNETLogo3.png)

## Overview

**GhostBot SpamStopper** is a robust and configurable IRC bot designed to monitor and prevent spam on IRC channels. Equipped with advanced detection patterns, automated responses, and powerful IRC service integration (NickServ and Operserv), GhostBot ensures a safe and spam-free environment for your IRC networks.

---

## Features

- **Spam Detection**: Identify spam messages using customizable regex patterns.
- **Automated Actions**: Use Operserv to execute actions like AKILL, GLINE, ZLINE, and more.
- **NickServ Authentication**: Secure bot nickname with NickServ.
- **Configurable Channels**: Join multiple channels and monitor them simultaneously.
- **Reputation System**: Keep track of users' reputation to determine their trustworthiness.
- **Reconnection Support**: Automatically reconnects after a disconnection.
- **Logging**: Comprehensive logging for monitoring and debugging.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python Libraries:
  ```bash
  pip3 install irc jaraco
  ```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gh0st68/SpamStopper.git
   cd SpamStopper
   ```

2. Edit configuration variables in the script to suit your network setup:
   - `IRC_SERVER`, `IRC_PORT`, `CHANNELS`
   - `NICKSERV_PASSWORD`, `OPERSERV_LOGIN`, `OPERSERV_PASSWORD`
   - `SPAM_KEYWORDS` (add or modify regex patterns)

3. Run the bot:
   ```bash
   python3 SpamStopper1.0.py &
   ```

---

## Configuration

### Key Settings

#### IRC Configuration
```python
IRC_SERVER = "irc.twistednet.org"  # IRC server address
IRC_PORT = 6697  # SSL port
CHANNELS = ["#twisssted", "#channel1", "#channel2"]  # Channels to join
BOT_NICKNAME = "GhostBot"  # Bot nickname
```

#### Authentication
- **NickServ**: Configure `NICKSERV_PASSWORD` to authenticate the bot's nickname.
- **Operserv**: Set `OPERSERV_LOGIN` and `OPERSERV_PASSWORD` for privileged actions.

#### Spam Detection
```python
SPAM_KEYWORDS = [
    r'irc\.ircnow\w*\.org',
    r'#SUPERBOWL\W*',
    r'sodomite',
    ...
]
```

#### Akill Configuration
Choose the type of action the bot should take against spammers:
```python
AKILL_TYPE = "operserv_akill_nick"  # Options: "operserv_gline_ip", "operserv_zline_ip", etc.
```

---

## Commands and Functionality

GhostBot comes with several commands that can be used in your channels to manage spam and user reputation:

- **!white add <nick>**: Adds a user to the whitelist.
- **!white remove <nick>**: Removes a user from the whitelist.
- **!stats**: Displays the bot's kill statistics.
- **Spam Detection**: Detects and handles spam messages in real-time.
- **NickServ Authentication**: Automatically authenticates using a secure password.
- **Operserv Integration**: Executes preconfigured actions (AKILL, GLINE, ZLINE) on detected spammers.
- **Reputation System**: Track user reputation and manage whitelist functionality.
- **Reconnection**: Recovers gracefully from disconnections.

---

## Running the Bot in a Screen Session

To run the bot in a detached screen session, follow these steps:

1. Install `screen` if it's not already installed:
   ```bash
   sudo apt install screen  # For Ubuntu/Debian
   ```

2. Start a new screen session:
   ```bash
   screen -S ghostbot
   ```

3. Inside the screen session, navigate to the bot's directory:
   ```bash
   cd SpamStopper
   ```

4. Start the bot:
   ```bash
   python3 SpamStopper1.0.py
   ```

5. To detach from the screen session and leave the bot running in the background, press:
   ```bash
   Ctrl + A, then D
   ```

6. To reattach to the screen session later, run:
   ```bash
   screen -r ghostbot
   ```

---

## Logging

Logs are stored in `ghostbot.log` and displayed in the console for real-time monitoring.

---

## Troubleshooting

1. **Connection Issues**:
   - Verify `IRC_SERVER` and `IRC_PORT` settings.
   - Ensure the IRC server allows SSL connections.

2. **Spam Patterns Not Matching**:
   - Update the `SPAM_KEYWORDS` list with more specific patterns.

3. **Authentication Problems**:
   - Double-check `NICKSERV_PASSWORD` and `OPERSERV_LOGIN`.

---

## Contribution

Contributions, suggestions, and bug reports are welcome! Fork the repository, make your changes, and submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For support or inquiries:
- Visit us on IRC at **irc.twistednet.org**.
- Join channels **#dev** and **#twisted** for help.
- Created and maintained by **gh0st**.
