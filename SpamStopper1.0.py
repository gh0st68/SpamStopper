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

# ----------------------------
# IRC Server Configuration
# ----------------------------
IRC_SERVER = "frozen.gh0st.boo"  # IRC server address
IRC_PORT = 6697  # IRC server port (typically 6697 for SSL)
CHANNELS = ["#g6", "#channel1", "#channel2"]  # List of channels to join
BOT_NICKNAME = "GhostBot"  # Bot's nickname
SERVICE_NICKNAME = "GhostBotServ"  # (unused, kept for reference)

# ----------------------------
# NickServ Configuration
# ----------------------------
NICKSERV_NICK = "NickServ"  
NICKSERV_PASSWORD = "your_nickserv_password"

# Define the NickServ authentication command template
NICKSERV_AUTH_COMMAND_TEMPLATE = "IDENTIFY {password}"

# ----------------------------
# IRC Operator (OPER) Configuration
# ----------------------------
OPER_USERNAME = "GhostBot"       # The oper username (often matches your bot's nick)
OPER_PASSWORD = "myoperpassword" # The oper password set in the IRCd config

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
    r'irc\.luatic\.net',
    r'irc\.supernets\.org'
]

# ----------------------------
# Logging Configuration
# ----------------------------
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

        # Create an SSL context that disables host checking and cert verification
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        irc.client.ServerConnection.buffer_class = buffer.LenientDecodingLineBuffer
        # Wrap the socket using our custom SSL context
        factory = irc.connection.Factory(wrapper=lambda sock: context.wrap_socket(sock, server_hostname=server))

        super().__init__([(server, port)], nickname, nickname, connect_factory=factory)
        self.channel_list = channels
        self.service_nick = service_nick
        self.spam_patterns = [re.compile(pattern, re.IGNORECASE | re.UNICODE) for pattern in SPAM_KEYWORDS]
        self.authenticated_nickserv = False
        self.opered_up = False  # Indicates if /oper succeeded

    def on_nicknameinuse(self, c, e):
        new_nick = c.get_nickname() + "_"
        logging.warning(f"Nickname '{c.get_nickname()}' is in use. Trying new nickname: {new_nick}")
        c.nick(new_nick)

    def on_welcome(self, c, e):
        logging.info(f"Connected to {IRC_SERVER}. Joining channels: {', '.join(self.channel_list)}")
        for channel in self.channel_list:
            c.join(channel)
            logging.info(f"Joined channel: {channel}")

        # Identify with NickServ first
        self.authenticate_nickserv(c)

    def authenticate_nickserv(self, connection):
        """
        Authenticate with NickServ to identify the bot's nickname.
        Afterward, do /oper if credentials are set.
        """
        if not self.authenticated_nickserv and NICKSERV_PASSWORD:
            auth_command = NICKSERV_AUTH_COMMAND_TEMPLATE.format(password=NICKSERV_PASSWORD)
            logging.info("Authenticating with NickServ...")
            connection.privmsg(NICKSERV_NICK, auth_command)
            self.authenticated_nickserv = True

            # Give NickServ a moment to process, then try /oper
            self.connection.execute_delayed(3, self.become_oper)  
        else:
            logging.error("NickServ password not set or already authenticated. NickServ auth skipped.")

    def become_oper(self):
        """
        Send the /oper command to become an IRC operator.
        """
        if not self.opered_up and OPER_USERNAME and OPER_PASSWORD:
            logging.info("Attempting to become IRC operator...")
            raw_oper_cmd = f"OPER {OPER_USERNAME} {OPER_PASSWORD}"
            self.connection.send_raw(raw_oper_cmd)
            # We can’t definitively know from this alone if the /oper succeeded, 
            # but we assume success if no error is received. 
            self.opered_up = True
        else:
            logging.warning("OPER username/password not set or already opered up.")

    def on_pubmsg(self, c, e):
        """
        Called when a public message is received in any joined channel.
        """
        message = e.arguments[0]
        source_channel = e.target
        sender = irc.client.NickMask(e.source).nick
        logging.info(f"Public message received in {source_channel} from {sender}: {message}")

        normalized_message = unicodedata.normalize('NFKC', message)
        for pattern in self.spam_patterns:
            if pattern.search(normalized_message):
                logging.info(f"Spam detected in public message in {source_channel} from {sender}: {message}")
                self.handle_spam(c, e, channel=source_channel)
                break

    def on_privmsg(self, c, e):
        """
        Called when a private message is received by the bot.
        """
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
        """
        Handles spam by issuing a kill or other oper-level command.
        """
        user = irc.client.NickMask(event.source).nick
        reason = "Spamming detected: Use of prohibited keywords."

        # Only attempt to KILL if we are opered up
        if not self.opered_up:
            logging.warning(f"Cannot KILL user {user}, bot is not opered up yet.")
            return

        try:
            # Issue a raw KILL command. You could do GLINE, ZLINE, etc. if your IRCd supports it.
            kill_cmd = f"KILL {user} :{reason}"
            logging.info(f"Sending kill command: {kill_cmd}")
            connection.send_raw(kill_cmd)

            # Optionally, let the channel know
            if not private and channel:
                connection.privmsg(channel, f"{user} has been killed for spamming.")
            elif not private:
                for ch in self.channel_list:
                    connection.privmsg(ch, f"{user} has been killed for spamming.")

        except Exception as ex:
            logging.error(f"Failed to handle spam for user {user}: {ex}")
            logging.error(traceback.format_exc())

    def on_disconnect(self, c, e):
        logging.warning(f"Disconnected from server. Reconnecting in 60 seconds...")
        time.sleep(60)
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
            logging.error(f"Reconnection failed: {ex}. Retrying in 60 seconds...")
            logging.error(traceback.format_exc())
            time.sleep(60)
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
