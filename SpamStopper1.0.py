#Spam Stopper 1.0 - by gh0st - irc.twistednet.org #dev #twisted

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
IRC_SERVER = "irc.twistednet.org"  # IRC server address
IRC_PORT = 6697  # IRC server port (typically 6697 for SSL)
CHANNELS = ["#twisssted", "#channel1", "#channel2"]  # List of channels to join
BOT_NICKNAME = "GhostBot"  # Bot's nickname in the channel
SERVICE_NICKNAME = "GhostBotServ"  # Bot's nickname used for service identification

# ----------------------------
# NickServ Configuration
# ----------------------------
NICKSERV_NICK = "NickServ"  # NickServ service nickname
NICKSERV_PASSWORD = "your_nickserv_password"  # NickServ password for the bot's nickname

# Define the NickServ authentication command template
# Typically: "/msg NickServ IDENTIFY <password>"
NICKSERV_AUTH_COMMAND_TEMPLATE = "IDENTIFY {password}"

# ----------------------------
# Operserv Configuration
# ----------------------------
OPERSERV_NICK = "Operserv"  # Operserv service nickname
OPERSERV_LOGIN = "your_operserv_login"  # Operserv login name
OPERSERV_PASSWORD = "your_operserv_password"  # Operserv password

# Define the Operserv authentication command template
# Adjust this template based on your IRCd's Operserv authentication method
# Example for InspIRCd: "/msg Operserv LOGIN <login> <password>"
OPERSERV_AUTH_COMMAND_TEMPLATE = "LOGIN {login} {password}"

# ----------------------------
# Spam Detection Configuration
# ----------------------------
# List of regex patterns to detect spam messages
# Add or modify patterns as needed
SPAM_KEYWORDS = [
    r'irc\.ircnow\w*\.org',  # Matches irc.ircnow.org, irc.ircnow1.org, etc.
    r'#SUPERBOWL\W*',  # Matches #SUPERBOWL followed by non-word characters
    r'#SUPER\W*',  # Matches #SUPER followed by non-word characters
    r'sodomite',  # Matches the word 'sodomite'
    r'LA\s*ST\s*WARNING',  # Matches variations like "LAST WARNING", "LA ST WARNING"
    r'LAST\?WARNING',  # Matches 'LAST?WARNING'
    r'SUPERNET',  # Matches 'SUPERNET'
    r'irc\.luatic\.net',  # Matches 'irc.luatic.net'
    r'irc\.supernets\.org'  # Matches 'irc.supernets.org'
    # Add more patterns as needed
]

# ----------------------------
# Akill Configuration
# ----------------------------
AKILL_ENABLED = True  # Set to False to disable akill functionality

# Define supported akill types
# Options:
# - "operserv_akill_nick": /msg Operserv AKILL add <nick> <reason>
# - "operserv_gline_ip": /msg Operserv GLINE add <ip> <duration> <reason>
# - "operserv_zline_ip": /msg Operserv ZLINE add <ip> <duration> <reason>
# - "operserv_block_nick": /msg Operserv BLOCK add <nick> <reason>
# - "operserv_kill_nick": /msg Operserv KILL add <nick> <reason>
# - "custom": User-defined command
AKILL_TYPE = "operserv_akill_nick"  # Change as needed

# Custom akill command template (used only if AKILL_TYPE is set to "custom")
# Use placeholders {nick}, {ip}, {duration}, {reason} as needed
AKILL_CUSTOM_COMMAND = "/msg Operserv akill add {nick} {reason}"  # Example: "/msg Operserv custom_command {nick} {reason}"

# Define akill command templates for supported types
AKILL_COMMAND_TEMPLATES = {
    "operserv_akill_nick": "/msg {operserv_nick} AKILL add {nick} {reason}",
    "operserv_gline_ip": "/msg {operserv_nick} GLINE add {ip} {duration} {reason}",
    "operserv_zline_ip": "/msg {operserv_nick} ZLINE add {ip} {duration} {reason}",
    "operserv_block_nick": "/msg {operserv_nick} BLOCK add {nick} {reason}",
    "operserv_kill_nick": "/msg {operserv_nick} KILL add {nick} {reason}",
    "custom": AKILL_CUSTOM_COMMAND  # User-defined
}

# ----------------------------
# Reconnection Settings
# ----------------------------
RECONNECT_DELAY = 60  # Seconds to wait before attempting to reconnect

# ============================
# Logging Configuration
# ============================
# Configure logging to log to both console and a file named 'ghostbot.log'
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
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
        # Ensure channels is a list
        if not isinstance(channels, list):
            raise ValueError("channels must be a list of channel names.")

        irc.client.ServerConnection.buffer_class = buffer.LenientDecodingLineBuffer
        factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
        super().__init__([(server, port)], nickname, nickname, connect_factory=factory)
        self.channel_list = channels  # Renamed from self.channels
        self.service_nick = service_nick
        self.spam_patterns = [re.compile(pattern, re.IGNORECASE | re.UNICODE) for pattern in SPAM_KEYWORDS]
        self.authenticated_nickserv = False
        self.authenticated_operserv = False

    def on_nicknameinuse(self, c, e):
        new_nick = c.get_nickname() + "_"
        logging.warning(f"Nickname '{c.get_nickname()}' is in use. Trying new nickname: {new_nick}")
        c.nick(new_nick)

    def on_welcome(self, c, e):
        logging.info(f"Connected to {IRC_SERVER}. Joining channels: {', '.join(self.channel_list)}")
        for channel in self.channel_list:
            c.join(channel)
            logging.info(f"Joined channel: {channel}")
        self.authenticate_nickserv(c)
        self.authenticate_operserv(c)

    def authenticate_nickserv(self, connection):
        """
        Authenticate with NickServ to identify the bot's nickname.
        """
        if not self.authenticated_nickserv and NICKSERV_PASSWORD:
            auth_command = NICKSERV_AUTH_COMMAND_TEMPLATE.format(password=NICKSERV_PASSWORD)
            logging.info("Authenticating with NickServ...")
            connection.privmsg(NICKSERV_NICK, auth_command)
            self.authenticated_nickserv = True
        elif not NICKSERV_PASSWORD:
            logging.error("NickServ password not set. NickServ authentication will be skipped.")

    def authenticate_operserv(self, connection):
        """
        Authenticate with Operserv to gain the ability to issue kill commands.
        """
        if not self.authenticated_operserv and OPERSERV_PASSWORD and OPERSERV_LOGIN:
            auth_command = OPERSERV_AUTH_COMMAND_TEMPLATE.format(login=OPERSERV_LOGIN, password=OPERSERV_PASSWORD)
            logging.info("Authenticating with Operserv...")
            connection.privmsg(OPERSERV_NICK, auth_command)
            self.authenticated_operserv = True
        elif not OPERSERV_PASSWORD or not OPERSERV_LOGIN:
            logging.error("Operserv login or password not set. Akill functionality may be limited.")

    def on_pubmsg(self, c, e):
        """
        Called when a public message is received in any of the joined channels.
        """
        message = e.arguments[0]
        source_channel = e.target  # The channel where the message was sent
        sender = irc.client.NickMask(e.source).nick
        logging.info(f"Public message received in {source_channel} from {sender}: {message}")
        # Normalize the message to NFKC to handle Unicode variations
        normalized_message = unicodedata.normalize('NFKC', message)
        # Check each spam pattern
        for pattern in self.spam_patterns:
            if pattern.search(normalized_message):
                logging.info(f"Spam detected in public message in {source_channel} from {sender}: {message}")
                self.handle_spam(c, e, channel=source_channel)
                break  # No need to check other patterns

    def on_privmsg(self, c, e):
        """
        Called when a private message is received by the bot.
        """
        message = e.arguments[0]
        sender = irc.client.NickMask(e.source).nick
        logging.info(f"Private message received from {sender}: {message}")
        # Normalize the message to NFKC to handle Unicode variations
        normalized_message = unicodedata.normalize('NFKC', message)
        # Check each spam pattern
        for pattern in self.spam_patterns:
            if pattern.search(normalized_message):
                logging.info(f"Spam detected in private message from {sender}: {message}")
                self.handle_spam(c, e, private=True)
                break  # No need to check other patterns

    def handle_spam(self, connection, event, private=False, channel=None):
        """
        Handles the spam by sending an akill command to Operserv based on the configured akill type.
        If private=True, the message was received as a private message.
        The 'channel' parameter specifies the channel where the spam was detected (if applicable).
        """
        if not AKILL_ENABLED:
            logging.info("Akill functionality is disabled. Skipping akill action.")
            return

        try:
            user = irc.client.NickMask(event.source).nick
            hostmask = irc.client.NickMask(event.source).host
            # Extract the IP address from the hostmask if possible
            ip = self.extract_ip(hostmask)
            reason = "Spamming detected: Use of prohibited keywords."
            duration = "0"  # Default duration; can be customized or made configurable

            # Debugging logs
            logging.debug(f"AKILL_COMMAND_TEMPLATES type: {type(AKILL_COMMAND_TEMPLATES)}")
            logging.debug(f"AKILL_TYPE: {AKILL_TYPE}")

            # Select the appropriate akill command template
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
                        operserv_nick=OPERSERV_NICK,
                        nick=user,
                        ip=ip,
                        duration=duration,
                        reason=reason
                    )
            else:
                logging.error(f"Unsupported AKILL_TYPE: {AKILL_TYPE}. Akill action aborted.")
                return

            logging.info(f"Sending akill command: {akill_command}")
            # Send the akill command to Operserv
            connection.privmsg(OPERSERV_NICK, akill_command)
            # Optionally, notify the channel or sender
            if not private and channel:
                connection.privmsg(channel, f"{user} has been removed for spamming.")
            elif not private:
                # If channel is not specified, notify all channels
                for ch in self.channel_list:
                    connection.privmsg(ch, f"{user} has been removed for spamming.")
            else:
                # Optionally, notify the sender privately (if appropriate)
                pass  # You can implement private notifications if desired
        except Exception as ex:
            logging.error(f"Failed to handle spam for user {user}: {ex}")
            logging.error(traceback.format_exc())

    def extract_ip(self, hostmask):
        """
        Extracts the IP address from the hostmask if possible.
        Returns the IP as a string or the full hostmask if IP extraction fails.
        """
        # Simple regex to extract IPv4 addresses
        ipv4_pattern = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
        match = ipv4_pattern.search(hostmask)
        if match:
            return match.group()
        else:
            # If IP extraction is not possible, return the hostmask
            logging.warning(f"Could not extract IP from hostmask: {hostmask}. Using hostmask instead.")
            return hostmask

    def on_disconnect(self, c, e):
        logging.warning(f"Disconnected from server. Reconnecting in {RECONNECT_DELAY} seconds...")
        time.sleep(RECONNECT_DELAY)
        self.reconnect()

    def reconnect(self):
        """
        Attempt to reconnect to the IRC server.
        """
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
    # Initialize and start the bot
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

