# MintyyBot 

MintyyBot is a feature-rich Discord bot built for **MintyyGal's** server, providing automated stream notifications, fun commands, and gaming utilities. It monitors YouTube and Twitch for live streams and new video uploads while also offering commands for fun interactions and community engagement.

## 🚀 Features
### 🔴 Stream Notifications
- Automatically announces when **MintyyGal** goes live on **YouTube** or **Twitch**.
- Notifies when a new **YouTube video** is uploaded.
- Sends an update when the streamer **goes offline**.

### 🎮 Gaming Commands
- `!randomagent` → Suggests a random **Valorant agent**.
- `!addgame` → Adds a game to the community game list (**Admin only**).
- `!removegame` → Removes a game from the list (**Admin only**).
- `!choosegame` → Randomly selects a game from the list.
- `!list` → Lists all available games.

### 🎭 Fun Commands
- `!hello` → Greets the user.
- `!joke` → Sends a random joke.

### 📡 Status Commands
- `!status` → Checks whether **MintyyGal** is currently live on Twitch or YouTube.

## 🛠 Installation
1. **Clone the Repository**
   ```sh
   git clone https://github.com/YOUR_GITHUB_USERNAME/MintyyBot.git
   cd MintyyBot
   ```
2. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Set up Environment Variables**
   Create a `.env` file in the root directory and add:
   ```ini
   DISCORD_BOT_TOKEN=your_discord_token
   YOUTUBE_API_KEY=your_youtube_api_key
   YOUTUBE_CHANNEL_ID=your_channel_id
   TWITCH_CLIENT_ID=your_twitch_client_id
   TWITCH_AUTH_TOKEN=your_twitch_auth_token
   TWITCH_USERNAME=your_twitch_username
   ```
4. **Run the Bot**
   ```sh
   python bot.py
   ```

## 🔧 Configuration & Permissions
- Ensure that the bot has the following **Discord permissions**:
  - `Send Messages`
  - `Read Messages`
  - `Embed Links`
  - `Manage Messages` (optional for moderation)
  - `Mention Everyone` (if needed)

## 💡 Usage
Simply **invite the bot** to your Discord server and start using the commands!
- Use `!hello` to get started.
- Add games with `!addgame` and remove them with `!removegame`.
- Check stream statuses using `!status`.

## 👨‍💻 Contributing
If you'd like to contribute to MintyyBot:
1. Fork the repository.
2. Create a new branch (`feature/your-feature`).
3. Commit your changes and push.
4. Open a pull request!

## 📜 License
This project is licensed under the **MIT License**.

---

### 🌟 Support
For any issues, suggestions, or feature requests, please open an **issue** on GitHub!

Happy chatting with MintyyBot! 🎀💖
