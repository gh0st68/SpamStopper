
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
- **Reputation System**: Keep track of users' reputation to determine their trustworthiness. Users with high reputation are trusted and exempt from removal.
- **Reconnection Support**: Automatically reconnects after a disconnection.
- **Logging**: Comprehensive logging for monitoring and debugging.

---

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python Libraries:
  ```bash
  pip3 install irc 
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
   python3 SpamStopper2.0.py &
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

## Options: AKILL, KLINE, GLINE, ZLINE

GhostBot offers several ways to take action against spammers:

### 1. **AKILL** (Account Kill)
- **Description**: This action involves banning a user from the network based on their nickname. It effectively prevents the user from reconnecting to any IRC server in the network using the same nickname. This is often used for persistent spammers who need to be permanently banned across the entire network.
- **Configuration**:
    ```python
    AKILL_ENABLED = True  # Enable AKILL functionality
    AKILL_TYPE = "operserv_akill_nick"  # Can be "operserv_akill_nick", or custom commands
    ```
- **Action**: AKILL can be configured to run automatically when spam is detected. It is sent to Operserv, which will apply the ban.

### 2. **KLINE** (Kill Line)
- **Description**: This action prevents a user from connecting to an IRC server based on their hostmask (hostname/IP). It is a local server ban and is typically used to block spammers from a specific server. Unlike AKILL, KLINE is limited to the server it's issued on.
- **Configuration**:
    ```python
    KLINE_ENABLED = True  # Enable KLINE functionality
    ```
- **Action**: When spam is detected, KLINE can be automatically triggered to block a specific IP or hostmask.

### 3. **GLINE** (Global Line)
- **Description**: GLINE is similar to KLINE but operates network-wide. This action is used to prevent users from connecting to any server in the network based on their IP address or hostmask.
- **Configuration**:
    ```python
    GLINE_ENABLED = True  # Enable GLINE functionality
    ```
- **Action**: GLINE is triggered when spam is detected, blocking the user’s IP globally across the network.

### 4. **ZLINE** (Z-Line)
- **Description**: ZLINE is a network-wide ban based on the user’s IP address. This action is more permanent than GLINE and is typically used for blocking large numbers of users or entire subnets.
- **Configuration**:
    ```python
    ZLINE_ENABLED = True  # Enable ZLINE functionality
    ```
- **Action**: When spam is detected, ZLINE can be triggered to block a user’s IP address across the entire network.

These actions can be selectively enabled or disabled, depending on your needs. You can also configure the bot to take multiple actions simultaneously, providing layered protection against spammers.

---

## Reputation System

### Overview
The **Reputation System** is designed to help the bot distinguish between malicious users and trusted ones. Users with a high reputation are less likely to be removed for spamming, and they may be whitelisted if needed. This system helps to prevent false positives and ensures that trusted users are not wrongfully penalized.

### Key Features
- **Reputation Score**: Each user has a reputation score that starts at 0. The score increases each time they participate in the network, especially when they trigger actions like spam detection.
- **Threshold for Trust**: Users with a reputation score above the **Reputation Threshold** are trusted and will not be affected by spam-related actions (e.g., AKILL, KLINE).
- **Whitelisting**: Users can be manually added to the whitelist, which exempts them from any spam checks or actions.

### How It Works
- The bot tracks users’ reputation over time by monitoring their activity and spam triggers. If a user accumulates enough positive reputation, they are considered trusted and will be exempt from automatic actions like AKILL or KLINE, regardless of their behavior.
- The **Reputation Threshold** is configurable, and once a user's reputation exceeds this threshold, the bot will no longer automatically remove them for spamming.

### Configuration
```python
DB_FILE = "ghostbot_reputation.db"  # SQLite database file for storing reputation data
REPUTATION_THRESHOLD = 5  # Users with reputation equal to or above this threshold are trusted and exempt from removal
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
