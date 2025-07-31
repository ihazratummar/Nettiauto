# Discord Car Finder Bot

This is an advanced Discord bot built using `discord.py` and `aiohttp`. It fetches car listings from provided URLs (e.g., used car marketplaces) based on dynamic, per-server filters such as year, price, kilometers, engine size, and engine type.

## 🚀 Features

- ✅ Multi-server support using `guild_id` based configuration
- 🔄 Periodic scraping (interval defined per guild)
- 🎯 Filters:
  - Year (min and max)
  - Price (min and max)
  - Kilometers (min and max)
  - Engine size (min and max)
  - Engine types (e.g., `bensiini`, `diesel`)
- 🧠 Uses `aiohttp` for async HTTP requests
- 🧩 Modular code with cogs
- 💬 Sends new matching car listings to a designated channel

## 🗂 Project Structure

```
car-finder-bot/
├── main.py              # Bot entry point
├── config.py            # Utility to load/save config
├── config.json          # Per-server filter & URL settings
├── cogs/
│   ├── fetcher.py       # Task to fetch and filter listings
│   └── commands.py      # Slash or prefix commands to manage URLs and filters
├── requirements.txt     # Dependencies list
├── LICENSE              # License info
└── README.md            # Project documentation
```

## 🛠 Setup Instructions

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure your bot token**
In `main.py`, insert your Discord bot token.

3. **Define server-specific filters**
Edit `config.json` to match your server needs. Example:
```json
{
  "1126486185947189318": {
    "channel_id": 1400076557934133369,
    "urls": [],
    "filters": {
      "year_min": 2000,
      "year_max": 2015,
      "price_min": 300,
      "price_max": 1300,
      "km_min": 50000,
      "km_max": 250000,
      "engine_size_min": 0.8,
      "engine_size_max": 1.8,
      "engine_type": ["bensiini", "diesel"]
    },
    "check_interval": 300
  }
}
```

4. **Run the bot**
```bash
python main.py
```

## 🧪 Todo

- [ ] Add pagination support for car listings
- [ ] Web dashboard to configure filters (via FastAPI or Flask)
- [ ] Command to manage filters via Discord

## 📝 License

MIT License. See [LICENSE](LICENSE) for more information.

---

Created with ❤️ by Hazrat Ummar Shaikh.
