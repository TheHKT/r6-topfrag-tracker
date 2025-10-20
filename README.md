# r6-topfrag-tracker
A small Python Discord bot helper that posts a player's most recent Rainbow Six Siege match and notifies if the player was the top fragger. Intended as a small utility — feel free to fork and improve.

## Features
- Fetches the latest match for a tracked R6 player
- Highlights whether the tracked player was the top fragger

## Installation
1. Clone the repo and open a terminal in the project folder:
   - PowerShell:
     ```
     git clone <repo-url>
     cd r6-topfrag-tracker
     ```
2. Install dependencies:
   - PowerShell:
     ```
     python -m pip install -r requirements.txt
     ```

## Configuration
Create a `.env` file in the repository root with these variables:

```
DISCORD_TOKEN=your_discord_bot_token
ALERT_CHANNEL_ID=discord_channel_id_to_post_to
R6_USERNAME=r6_player_username_to_track
```

- DISCORD_TOKEN: Bot token from the Discord Developer Portal.
- ALERT_CHANNEL_ID: Channel ID where the bot will send updates.
- R6_USERNAME: The in-game username to monitor.

## Running
Start the bot from the project root:

- PowerShell / CMD:
  ```
  python bot.py
  ```

The bot will log status to the console. Check the output for connection and match-check messages.

## Contributing
Contributions welcome. Suggestions:
- Support multiple tracked users
- Add richer match embeds (map, round breakdown, operator)
- Cache handling and rate-limit resilience

Please open issues or PRs with a clear description and tests where applicable.