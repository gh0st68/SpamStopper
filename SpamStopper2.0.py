#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssl
import irc.bot
import irc.connection
import time
import re
import unicodedata
import logging
import traceback
from jaraco.stream import buffer
import sqlite3

# ============================
# Configuration Variables
# ============================

# ----------------------------
# IRC Server Configuration
# ----------------------------
IRC_SERVER = "prism.twistednet.org"  # The server to connect to
IRC_PORT = 6697  # The port for SSL connection
CHANNELS = ["#SDASD", "#dev", "#konnect-chat", "#valyria", "#ai", "#sadkjksdj"]  # List of channels the bot will join
BOT_NICKNAME = "GhostBot"  # The bot's nickname
SERVICE_NICKNAME = "GhostBotServ"  # The bot's service nickname

# ----------------------------
# NickServ Configuration
# ----------------------------
NICKSERV_NICK = "NickServ"  # The nickname of NickServ for authentication
NICKSERV_PASSWORD = "your_nickserv_password"  # The password for NickServ authentication
NICKSERV_AUTH_COMMAND_TEMPLATE = "IDENTIFY {password}"  # Template for NickServ authentication command

# ----------------------------
# IRC Oper Configuration
# ----------------------------
IRC_OPER_USERNAME = "HACKTEHPLANET"  # IRC operator username
IRC_OPER_PASSWORD = "CHANGEME"  # IRC operator password

# ----------------------------
# Spam Detection Configuration
# ----------------------------
SPAM_KEYWORDS = [
    r'irc\.ircnow\w*\.org',  # Matches irc.ircnow.org, irc.ircnow1.org, etc.
    r'#SUPERBOWL\W*',  # Matches #SUPERBOWL followed by non-word characters
    r'#SUPER\W*',  # Matches #SUPER followed by non-word characters
    r'sodomite',  # Matches the word 'sodomite'
    r'LA\s*ST\s*WARNING',  # Matches variations like "LAST WARNING", "LA ST WARNING"
    r'LAST\?WARNING',  # Matches 'LAST?WARNING'
    r'SUPERNET',  # Matches 'SUPERNET'
    r'irc\.luatic\.net',  # Matches 'irc.luatic.net'
    r'irc\.supernets\.org',  # Matches 'irc.supernets.org'
    r'(?<!\S)\.\'\'\.(?!\S)',  # Matches standalone .''.
    r'[\x80-\xff]{3,}',  # Matches sequences of non-ASCII characters (3 or more)
    r'(\W){4,}',  # Matches 4 or more consecutive non-word characters
    r'\b0x[a-fA-F0-9]+\b',  # Matches hexadecimal text (e.g., 0xAA0)
    r'[^\x20-\x7E]{3,}',  # Matches non-printable ASCII characters (3 or more)
    r'(.)\1{6,}',  # Matches any character repeated 6 or more times
    r'(\s*[^a-zA-Z0-9\s]+){4,}'  # Matches sequences of special characters (4 or more)
]

# ----------------------------
# Akill / Kill Configuration
# ----------------------------
AKILL_ENABLED = False  # Set to False to disable akill functionality
KILL_ENABLED = True  # Set to True to enable raw server KILL commands

AKILL_TYPE = "operserv_akill_nick"  # Type of akill to perform (e.g., "operserv_akill_nick")
AKILL_CUSTOM_COMMAND = "akill add {nick} {reason}"  # Custom akill command template

AKILL_COMMAND_TEMPLATES = {
    "operserv_akill_nick": "AKILL add {nick} {reason}",
    "operserv_gline_ip":   "GLINE add {ip} {duration} {reason}",
    "operserv_zline_ip":   "ZLINE add {ip} {duration} {reason}",
    "operserv_block_nick": "BLOCK add {nick} {reason}",
    "operserv_kill_nick":  "KILL add {nick} {reason}",
    "custom": AKILL_CUSTOM_COMMAND
}

# ----------------------------
# Reconnection Settings
# ----------------------------
RECONNECT_DELAY = 60  # Delay (in seconds) before reconnecting after disconnection

# ----------------------------
# Logging Configuration
# ----------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ghostbot.log"),  # Logs to a file
        logging.StreamHandler()  # Logs to the console
    ]
)

# ----------------------------
# Reputation System Configuration
# ----------------------------
DB_FILE = "ghostbot_reputation.db"  # SQLite database file for storing reputation data
REPUTATION_THRESHOLD = 5  # Users with reputation equal to or above this threshold are trusted and exempt from removal

# ============================
# Reputation System Functions
# ============================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_reputation (
            nick TEXT PRIMARY KEY,
            score INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_reputation(nick):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM user_reputation WHERE nick = ?", (nick,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO user_reputation (nick, score) VALUES (?, ?)", (nick, 0))
        conn.commit()
        conn.close()
        return 0
    else:
        conn.close()
        return row[0]

def increment_reputation(nick, amount=1):
    current_score = get_reputation(nick)
    new_score = current_score + amount

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE user_reputation SET score = ? WHERE nick = ?", (new_score, nick))
    conn.commit()
    conn.close()
    return new_score

def is_trusted(nick):
    return get_reputation(nick) >= REPUTATION_THRESHOLD

# ============================
# GhostBot Class Definition
# ============================

class GhostBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channels, nickname, service_nick, server, port=6697):
        if not isinstance(channels, list):
            raise ValueError("channels must be a list of channel names.")

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        irc.client.ServerConnection.buffer_class = buffer.LenientDecodingLineBuffer
        factory = irc.connection.Factory(wrapper=ssl_context.wrap_socket)

        super().__init__([(server, port)], nickname, nickname, connect_factory=factory)

        self.channel_list = channels
        self.service_nick = service_nick
        self.spam_patterns = [re.compile(pattern, re.IGNORECASE | re.UNICODE) for pattern in SPAM_KEYWORDS]
        self.authenticated_nickserv = False
        self.whitelist = ["w"]
        self.kill_stats = []

    def on_nicknameinuse(self, c, e):
        new_nick = c.get_nickname() + "_"
        logging.warning(f"Nickname '{c.get_nickname()}' is in use. Trying new nickname: {new_nick}")
        c.nick(new_nick)

    def on_welcome(self, c, e):
        logging.info(f"Connected to {IRC_SERVER}.")
        if IRC_OPER_USERNAME and IRC_OPER_PASSWORD:
            logging.info(f"Performing IRC oper command: /oper {IRC_OPER_USERNAME} [password hidden]")
            c.oper(IRC_OPER_USERNAME, IRC_OPER_PASSWORD)
        for channel in self.channel_list:
            c.join(channel)
            logging.info(f"Joined channel: {channel}")
        self.authenticate_nickserv(c)

    def authenticate_nickserv(self, connection):
        if not self.authenticated_nickserv and NICKSERV_PASSWORD:
            auth_command = NICKSERV_AUTH_COMMAND_TEMPLATE.format(password=NICKSERV_PASSWORD)
            logging.info("Authenticating with NickServ...")
            connection.privmsg(NICKSERV_NICK, auth_command)
            self.authenticated_nickserv = True
        elif not NICKSERV_PASSWORD:
            logging.error("NickServ password not set. NickServ authentication will be skipped.")

    def on_pubmsg(self, c, e):
        message = e.arguments[0]
        source_channel = e.target
        sender = irc.client.NickMask(e.source).nick
        logging.info(f"Public message received in {source_channel} from {sender}: {message}")

        if message.startswith('!'):
            self.handle_command(message, sender, source_channel)

        normalized_message = unicodedata.normalize('NFKC', message)
        for pattern in self.spam_patterns:
            if pattern.search(normalized_message):
                logging.info(f"Spam detected in {source_channel} from {sender}: {message}")
                self.handle_spam(c, e, channel=source_channel)
                return

        increment_reputation(sender)

    def on_privmsg(self, c, e):
        message = e.arguments[0]
        sender = irc.client.NickMask(e.source).nick
        logging.info(f"Private message received from {sender}: {message}")

        normalized_message = unicodedata.normalize('NFKC', message)
        for pattern in self.spam_patterns:
            if pattern.search(normalized_message):
                logging.info(f"Spam detected in private message from {sender}: {message}")
                self.handle_spam(c, e, private=True)
                return

        increment_reputation(sender)

    def handle_command(self, message, sender, channel):
        parts = message.split()
        cmd = parts[0][1:].lower()
        args = parts[1:]

        if cmd == "white":
            self.handle_whitelist_command(args, sender, channel)
        elif cmd == "stats":
            self.handle_stats_command(sender, channel)

    def handle_whitelist_command(self, args, sender, channel):
        if len(args) < 2:
            self.connection.privmsg(
                channel,
                "\x0304[Error]\x03 Usage: !white add <nick> or !white remove <nick>"
            )
            return

        action = args[0].lower()
        nick_to_modify = args[1]

        if action == "add":
            if nick_to_modify not in self.whitelist:
                self.whitelist.append(nick_to_modify)
                self.connection.privmsg(
                    channel,
                    f"\x032[Whitelist]\x03 Added \x02{nick_to_modify}\x02 to the whitelist."
                )
            else:
                self.connection.privmsg(
                    channel,
                    f"\x0307[Whitelist]\x03 \x02{nick_to_modify}\x02 is already whitelisted."
                )

        elif action == "remove":
            if nick_to_modify in self.whitelist:
                self.whitelist.remove(nick_to_modify)
                self.connection.privmsg(
                    channel,
                    f"\x032[Whitelist]\x03 Removed \x02{nick_to_modify}\x02 from the whitelist."
                )
            else:
                self.connection.privmsg(
                    channel,
                    f"\x0304[Error]\x03 \x02{nick_to_modify}\x02 was not found in the whitelist."
                )
        else:
            self.connection.privmsg(
                channel,
                "\x0304[Error]\x03 Unknown action. Use: add/remove"
            )

    def handle_stats_command(self, sender, channel):
        if not self.kill_stats:
            self.connection.privmsg(channel, "\x0313[Stats]\x03 No kills recorded yet.")
            return

        self.connection.privmsg(channel, "\x02\x0311[Kill Stats]\x03\x02")
        for entry in self.kill_stats:
            kill_line = (
                f"\x0309Nick:\x03 \x02{entry['nick']}\x02 | "
                f"\x0309Channel:\x03 \x02{entry['channel']}\x02 | "
                f"\x0309Reason:\x03 \x02{entry['reason']}\x02 | "
                f"\x0309Timestamp:\x03 \x02{entry['timestamp']}\x02"
            )
            self.connection.privmsg(channel, kill_line)

    def handle_spam(self, connection, event, private=False, channel=None):
        user = irc.client.NickMask(event.source).nick

        if user in self.whitelist:
            logging.info(f"Skipping spam check for whitelisted user: {user}")
            return

        if is_trusted(user):
            logging.info(f"Trusted user '{user}' triggered spam but is above threshold. Skipping removal.")
            return

        reason = "Spamming detected: Use of prohibited keywords."
        duration = "0"

        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.kill_stats.append({
            "nick": user,
            "channel": channel if channel else "PrivateMessage",
            "reason": reason,
            "timestamp": timestamp_str
        })

        if not AKILL_ENABLED and not KILL_ENABLED:
            logging.info("Akill and Kill are disabled. No action taken.")
            return

        try:
            if AKILL_ENABLED:
                if AKILL_TYPE in AKILL_COMMAND_TEMPLATES:
                    if AKILL_TYPE == "custom":
                        akill_command = AKILL_COMMAND_TEMPLATES["custom"].format(
                            nick=user,
                            ip="",
                            duration=duration,
                            reason=reason
                        )
                    else:
                        akill_command = AKILL_COMMAND_TEMPLATES[AKILL_TYPE].format(
                            operserv_nick="Operserv",
                            nick=user,
                            ip="",
                            duration=duration,
                            reason=reason
                        )
                else:
                    logging.error(f"Unsupported AKILL_TYPE: {AKILL_TYPE}. Akill action aborted.")
                    return

                logging.info(f"Sending akill command: {akill_command}")
                connection.privmsg("Operserv", akill_command)

            if KILL_ENABLED:
                kill_command = f"KILL {user} {reason}"
                logging.info(f"Sending kill command: {kill_command}")
                connection.send_raw(kill_command)

            removal_msg = f"\x034{user}\x03 has been \x02removed\x02 for spamming."
            if not private and channel:
                connection.privmsg(channel, removal_msg)
            elif not private:
                for ch in self.channel_list:
                    connection.privmsg(ch, removal_msg)

        except Exception as ex:
            logging.error(f"Failed to handle spam for user {user}: {ex}")
            logging.error(traceback.format_exc())

    def extract_ip(self, hostmask):
        ipv4_pattern = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
        match = ipv4_pattern.search(hostmask)
        if match:
            return match.group()
        else:
            logging.warning(f"Could not extract IP from hostmask: {hostmask}. Using hostmask instead.")
            return hostmask

    def on_disconnect(self, c, e):
        logging.warning(f"Disconnected from server. Reconnecting in {RECONNECT_DELAY} seconds...")
        time.sleep(RECONNECT_DELAY)
        self.reconnect()

    def reconnect(self):
        try:
            logging.info("Attempting to reconnect...")
            self.connect(IRC_SERVER, IRC_PORT, BOT_NICKNAME)
            self.start()
        except Exception as ex:
            logging.error(f"Reconnection failed: {ex}. Retrying in {RECONNECT_DELAY} seconds...")
            logging.error(traceback.format_exc())
            time.sleep(RECONNECT_DELAY)
            self.reconnect()

def main():
    try:
        init_db()
        bot = GhostBot(CHANNELS, BOT_NICKNAME, SERVICE_NICKNAME, IRC_SERVER, IRC_PORT)
        logging.info("Starting GhostBot...")
        bot.start()
    except KeyboardInterrupt:
        logging.info("Bot shutting down gracefully.")
    except Exception as ex:
        logging.error(f"An error occurred: {ex}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    main()
