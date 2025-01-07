#Spam Stopper 1.0 - by gh0st - irc.twistednet.org #dev #twisted


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

# ============================
# Configuration Variables
# ============================

# ----------------------------
# IRC Server Configuration
# ----------------------------
IRC_SERVER = "irc.twistednet.org"
IRC_PORT = 6697
CHANNELS = ["#g6", "#channel1", "#channel2"]
BOT_NICKNAME = "GhostBot"
SERVICE_NICKNAME = "GhostBotServ"

# ----------------------------
# NickServ Configuration
# ----------------------------
NICKSERV_NICK = "NickServ"
NICKSERV_PASSWORD = "your_nickserv_password"
NICKSERV_AUTH_COMMAND_TEMPLATE = "IDENTIFY {password}"

# ----------------------------
# IRC Oper Configuration
# ----------------------------
IRC_OPER_USERNAME = "gh0st"
IRC_OPER_PASSWORD = "changeme"

# ----------------------------
# Spam Detection Configuration
# ----------------------------
SPAM_KEYWORDS = [
    r'irc\.ircnow\w*\.org',
    r'#SUPERBOWL\W*',
    r'#SUPER\W*',
    r'sodomite',
    r'LA\s*ST\s*WARNING',
    r'LAST\?WARNING',
    r'SUPERNET',
    r'ꜱᴜᴘᴇʀɴᴇᴛꜱ',
    r'irc\.luatic\.net',
    r'irc\.supernets\.org',
    r'\s*\.\'\'\.\s*\n\s*.*\s*\*\*.*:_\\/_:\s*\n\s*:.*:_\\/_:.*:\s*'
]


# ----------------------------
# Akill / Kill Configuration
# ----------------------------
AKILL_ENABLED = True  # Set to False to disable akill functionality
KILL_ENABLED = False  # (ADDED) Set to True to enable raw server KILL commands

# Define supported akill types
AKILL_TYPE = "operserv_akill_nick"  # e.g. "operserv_akill_nick", "operserv_kill_nick", etc.

AKILL_CUSTOM_COMMAND = "akill add {nick} {reason}"

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
RECONNECT_DELAY = 60

# ============================
# Logging Configuration
# ============================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ghostbot.log"),
        logging.StreamHandler()
    ]
)


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

    def on_nicknameinuse(self, c, e):
        new_nick = c.get_nickname() + "_"
        logging.warning(f"Nickname '{c.get_nickname()}' is in use. Trying new nickname: {new_nick}")
        c.nick(new_nick)

    def on_welcome(self, c, e):
        logging.info(f"Connected to {IRC_SERVER}.")

        # Attempt to become an IRC operator
        if IRC_OPER_USERNAME and IRC_OPER_PASSWORD:
            logging.info(f"Performing IRC oper command: /oper {IRC_OPER_USERNAME} [password hidden]")
            c.oper(IRC_OPER_USERNAME, IRC_OPER_PASSWORD)

        # Join channels
        for channel in self.channel_list:
            c.join(channel)
            logging.info(f"Joined channel: {channel}")

        # Authenticate with NickServ
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

        normalized_message = unicodedata.normalize('NFKC', message)

        for pattern in self.spam_patterns:
            if pattern.search(normalized_message):
                logging.info(f"Spam detected in {source_channel} from {sender}: {message}")
                self.handle_spam(c, e, channel=source_channel)
                break

    def on_privmsg(self, c, e):
        message = e.arguments[0]
        sender = irc.client.NickMask(e.source).nick
        logging.info(f"Private message received from {sender}: {message}")

        normalized_message = unicodedata.normalize('NFKC', message)

        for pattern in self.spam_patterns:
            if pattern.search(normalized_message):
                logging.info(f"Spam detected in private message from {sender}: {message}")
                self.handle_spam(c, e, private=True)
                break

    def handle_spam(self, connection, event, private=False, channel=None):
        if not AKILL_ENABLED and not KILL_ENABLED:
            # (ADDED) If both are disabled, do nothing.
            logging.info("Akill and Kill are disabled. No action taken.")
            return

        user = irc.client.NickMask(event.source).nick
        hostmask = irc.client.NickMask(event.source).host
        ip = self.extract_ip(hostmask)
        reason = "Spamming detected: Use of prohibited keywords."
        duration = "0"

        # (ADDED) If KILL_ENABLED is True, do a raw server kill
        if not AKILL_ENABLED and KILL_ENABLED:
            # Use raw server KILL command (bypassing services)
            kill_command = f"KILL {user} :{reason}"
            logging.info(f"Sending raw KILL command: {kill_command}")
            connection.send_raw(kill_command)

            # Optionally notify the channel(s)
            if not private and channel:
                connection.privmsg(channel, f"{user} has been KILLed for spamming (raw server kill).")
            elif not private:
                for ch in self.channel_list:
                    connection.privmsg(ch, f"{user} has been KILLed for spamming (raw server kill).")

            return

        # (CHANGED) Otherwise, if AKILL_ENABLED is True, do normal akill logic
        try:
            if AKILL_TYPE in AKILL_COMMAND_TEMPLATES:
                if AKILL_TYPE == "custom":
                    akill_command = AKILL_COMMAND_TEMPLATES["custom"].format(
                        nick=user,
                        ip=ip,
                        duration=duration,
                        reason=reason
                    )
                else:
                    akill_command = AKILL_COMMAND_TEMPLATES[AKILL_TYPE].format(
                        operserv_nick="Operserv",  # Not necessarily used in the string
                        nick=user,
                        ip=ip,
                        duration=duration,
                        reason=reason
                    )
            else:
                logging.error(f"Unsupported AKILL_TYPE: {AKILL_TYPE}. Akill action aborted.")
                return

            logging.info(f"Sending akill command: {akill_command}")
            connection.privmsg("Operserv", akill_command)

            if not private and channel:
                connection.privmsg(channel, f"{user} has been removed for spamming.")
            elif not private:
                for ch in self.channel_list:
                    connection.privmsg(ch, f"{user} has been removed for spamming.")

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


# ============================
# Main Function
# ============================
def main():
    try:
        bot = GhostBot(CHANNELS, BOT_NICKNAME, SERVICE_NICKNAME, IRC_SERVER, IRC_PORT)
        logging.info("Starting GhostBot...")
        bot.start()
    except KeyboardInterrupt:
        logging.info("Bot shutting down gracefully.")
    except Exception as ex:
        logging.error(f"An error occurred: {ex}")
        logging.error(traceback.format_exc())


# ============================
# Entry Point
# ============================
if __name__ == "__main__":
    main()


