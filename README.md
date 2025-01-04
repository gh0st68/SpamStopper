<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spam Stopper Bot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        header {
            background: #222;
            color: #fff;
            padding: 20px 10%;
            text-align: center;
        }
        header h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        header p {
            margin: 10px 0 0;
        }
        section {
            padding: 20px 10%;
        }
        h2 {
            color: #222;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
        }
        pre {
            background: #f4f4f4;
            padding: 10px;
            border-left: 5px solid #ddd;
            overflow-x: auto;
        }
        ul {
            margin: 20px 0;
            padding-left: 20px;
        }
        li {
            margin: 10px 0;
        }
        footer {
            background: #222;
            color: #fff;
            text-align: center;
            padding: 10px;
            margin-top: 20px;
        }
        footer p {
            margin: 0;
        }
        a {
            color: #007BFF;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .code-block {
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            font-family: monospace;
            font-size: 0.9rem;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <header>
        <h1>Spam Stopper Bot</h1>
        <p>A powerful and customizable Python-based IRC bot for spam detection, NickServ authentication, and moderation.</p>
    </header>
    <section>
        <h2>Features</h2>
        <ul>
            <li>Automatic NickServ and Operserv authentication.</li>
            <li>Spam detection using customizable regex patterns.</li>
            <li>Handles spam in both public and private messages.</li>
            <li>Supports multiple akill types, including custom commands.</li>
            <li>Robust logging for monitoring and debugging.</li>
            <li>Graceful reconnection handling.</li>
            <li>Easy-to-configure settings for server, credentials, and behavior.</li>
        </ul>
    </section>
    <section>
        <h2>Installation</h2>
        <p>To use Spam Stopper Bot, follow these steps:</p>
        <ol>
            <li>Clone the repository to your local machine:</li>
            <pre class="code-block">git clone https://github.com/yourusername/SpamStopperBot.git</pre>
            <li>Navigate to the project directory:</li>
            <pre class="code-block">cd SpamStopperBot</pre>
            <li>Install the required dependencies:</li>
            <pre class="code-block">pip install irc jaraco.stream</pre>
            <li>Configure the bot by editing the <code>SpamStopperBot.py</code> file with your IRC server and authentication details.</li>
            <li>Run the bot:</li>
            <pre class="code-block">python SpamStopperBot.py</pre>
        </ol>
    </section>
    <section>
        <h2>Configuration</h2>
        <p>All configuration variables are located at the top of the <code>SpamStopperBot.py</code> file. Below are some key settings:</p>
        <ul>
            <li><strong>IRC Server:</strong> Set the IRC server, port, and channel.</li>
            <li><strong>NickServ:</strong> Configure your NickServ nickname and password for authentication.</li>
            <li><strong>Operserv:</strong> Configure your Operserv login and password for issuing akill commands.</li>
            <li><strong>Spam Keywords:</strong> Add or modify spam detection regex patterns.</li>
            <li><strong>Akill Configuration:</strong> Enable/disable akill and customize command formats.</li>
        </ul>
        <p>Example configuration:</p>
        <pre class="code-block">
IRC_SERVER = "irc.example.com"
IRC_PORT = 6697
CHANNEL = "#example-channel"
BOT_NICKNAME = "SpamStopperBot"
NICKSERV_PASSWORD = "your_password"
OPERSERV_LOGIN = "your_operserv_login"
OPERSERV_PASSWORD = "your_operserv_password"
        </pre>
    </section>
    <section>
        <h2>Usage</h2>
        <p>Once the bot is running, it will:</p>
        <ul>
            <li>Authenticate with NickServ to identify its nickname.</li>
            <li>Authenticate with Operserv (if credentials are provided).</li>
            <li>Monitor messages in the configured channel and private messages for spam.</li>
            <li>Take appropriate action (e.g., akill) if spam is detected.</li>
        </ul>
        <p>Spam patterns and actions are fully customizable through the configuration section.</p>
    </section>
    <section>
        <h2>Help and Support</h2>
        <p>If you need help or want to learn more about the bot, join us on <code>irc.twistednet.org</code>:</p>
        <ul>
            <li><strong>Channel:</strong> <code>#dev</code></li>
            <li><strong>Channel:</strong> <code>#twisted</code></li>
        </ul>
        <p>We'd love to hear from you!</p>
    </section>
    <section>
        <h2>Credits</h2>
        <p>The Spam Stopper Bot was created by <strong>gh0st</strong>.</p>
    </section>
    <footer>
        <p>Created with ❤️ by <a href="https://github.com/yourusername" target="_blank">gh0st</a>. Licensed under MIT.</p>
    </footer>
</body>
</html>
