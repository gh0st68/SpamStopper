<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GhostBot SpamStopper</title>
</head>
<body>
    <header>
        <h1>GhostBot SpamStopper</h1>
        <img src="https://raw.githubusercontent.com/gh0st68/web/main/TwistedNETLogo3.png" alt="GhostBot Logo" style="max-width: 300px;">
    </header>

    <section>
        <h2>Overview</h2>
        <p>
            <strong>GhostBot SpamStopper</strong> is a robust and configurable IRC bot designed to monitor and prevent spam on IRC channels.
            Equipped with advanced detection patterns, automated responses, and powerful IRC service integration (NickServ and Operserv),
            GhostBot ensures a safe and spam-free environment for your IRC networks.
        </p>
    </section>

    <section>
        <h2>Features</h2>
        <ul>
            <li><strong>Spam Detection:</strong> Identify spam messages using customizable regex patterns.</li>
            <li><strong>Automated Actions:</strong> Use Operserv to execute actions like AKILL, GLINE, ZLINE, and more.</li>
            <li><strong>NickServ Authentication:</strong> Secure bot nickname with NickServ.</li>
            <li><strong>Configurable Channels:</strong> Join multiple channels and monitor them simultaneously.</li>
            <li><strong>Reconnection Support:</strong> Automatically reconnects after a disconnection.</li>
            <li><strong>Logging:</strong> Comprehensive logging for monitoring and debugging.</li>
        </ul>
    </section>

    <section>
        <h2>Getting Started</h2>
        <h3>Prerequisites</h3>
        <ul>
            <li>Python 3.8+</li>
            <li>Required Python Libraries:
                <pre><code>pip install irc python-jaraco</code></pre>
            </li>
        </ul>

        <h3>Installation</h3>
        <ol>
            <li>Clone the repository:
                <pre><code>git clone https://github.com/gh0st68/SpamStopper.git
cd SpamStopper</code></pre>
            </li>
            <li>Edit configuration variables in the script to suit your network setup:
                <ul>
                    <li><code>IRC_SERVER</code>, <code>IRC_PORT</code>, <code>CHANNELS</code></li>
                    <li><code>NICKSERV_PASSWORD</code>, <code>OPERSERV_LOGIN</code>, <code>OPERSERV_PASSWORD</code></li>
                    <li><code>SPAM_KEYWORDS</code> (add or modify regex patterns)</li>
                </ul>
            </li>
            <li>Run the bot:
                <pre><code>python3 ghostbot.py</code></pre>
            </li>
        </ol>
    </section>

    <section>
        <h2>Configuration</h2>
        <h3>Key Settings</h3>
        <h4>IRC Configuration</h4>
        <pre><code>IRC_SERVER = "irc.twistednet.org"  # IRC server address
IRC_PORT = 6697  # SSL port
CHANNELS = ["#twisssted", "#channel1", "#channel2"]  # Channels to join
BOT_NICKNAME = "GhostBot"  # Bot nickname</code></pre>

        <h4>Authentication</h4>
        <ul>
            <li><strong>NickServ:</strong> Configure <code>NICKSERV_PASSWORD</code> to authenticate the bot's nickname.</li>
            <li><strong>Operserv:</strong> Set <code>OPERSERV_LOGIN</code> and <code>OPERSERV_PASSWORD</code> for privileged actions.</li>
        </ul>

        <h4>Spam Detection</h4>
        <pre><code>SPAM_KEYWORDS = [
    r'irc\.ircnow\w*\.org',
    r'#SUPERBOWL\W*',
    r'sodomite',
    ...
]</code></pre>

        <h4>Akill Configuration</h4>
        <p>Choose the type of action the bot should take against spammers:</p>
        <pre><code>AKILL_TYPE = "operserv_akill_nick"  # Options: "operserv_gline_ip", "operserv_zline_ip", etc.</code></pre>
    </section>

    <section>
        <h2>Commands and Functionality</h2>
        <ul>
            <li><strong>Spam Detection:</strong> Detect and handle spam messages in real-time.</li>
            <li><strong>NickServ Authentication:</strong> Automatically authenticates using a secure password.</li>
            <li><strong>Operserv Integration:</strong> Executes preconfigured actions on detected spammers.</li>
            <li><strong>Reconnection:</strong> Recovers gracefully from disconnections.</li>
        </ul>
    </section>

    <section>
        <h2>Logging</h2>
        <p>Logs are stored in <code>ghostbot.log</code> and displayed in the console for real-time monitoring.</p>
    </section>

    <section>
        <h2>Troubleshooting</h2>
        <ol>
            <li><strong>Connection Issues:</strong>
                <ul>
                    <li>Verify <code>IRC_SERVER</code> and <code>IRC_PORT</code> settings.</li>
                    <li>Ensure the IRC server allows SSL connections.</li>
                </ul>
            </li>
            <li><strong>Spam Patterns Not Matching:</strong>
                <p>Update the <code>SPAM_KEYWORDS</code> list with more specific patterns.</p>
            </li>
            <li><strong>Authentication Problems:</strong>
                <p>Double-check <code>NICKSERV_PASSWORD</code> and <code>OPERSERV_LOGIN</code>.</p>
            </li>
        </ol>
    </section>

    <section>
        <h2>Contribution</h2>
        <p>Contributions, suggestions, and bug reports are welcome! Fork the repository, make your changes, and submit a pull request.</p>
    </section>

    <section>
        <h2>License</h2>
        <p>This project is licensed under the MIT License. See the <a href="LICENSE">LICENSE</a> file for details.</p>
    </section>

    <section>
        <h2>Contact</h2>
        <p>For support or inquiries:</p>
        <ul>
            <li>Visit us on IRC at <strong>irc.twistednet.org</strong>.</li>
            <li>Join channels <strong>#dev</strong> and <strong>#twisted</strong> for help.</li>
            <li>Created and maintained by <strong>gh0st</strong>.</li>
        </ul>
    </section>
</body>
</html>
