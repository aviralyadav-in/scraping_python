# Telegram Deals Channel Scraper

## Project Description

Telegram Deals Channel Scraper is a Python automation project that connects to Telegram using the Telethon library and extracts deal information from Telegram deals channels.

The scraper collects:
- Message ID
- Post date
- Deal content
- Product link
- Product image
- Channel name

The extracted data is stored in JSON format, and product images are downloaded into a local images folder.

---

## Technologies Used

- Python 3.9+
- Telethon
- Telegram MTProto API
- JSON
- Async Programming

---

## Features

- Connects to Telegram using a real user account
- Scrapes messages from selected Telegram channels
- Extracts product links from messages and buttons
- Downloads attached product images
- Saves data into `deals.json`
- Maintains execution logs in `log.json`
- Prevents duplicate message scraping
- Handles Telegram API rate limits using FloodWaitError
- Uses configuration file for easy setup

---

## Project Structure


TelegramScraper/

├── telegram_deals_scraper.py # Main scraper file
├── config.json # Configuration settings
├── requirements.txt # Required Python packages
├── README.md # Project documentation

├── deals.json # Scraped deal data
├── log.json # Execution logs

├── images/ # Downloaded images
│
├── session.session # Telegram login session
│
└── venv/ # Virtual environment


---

## Requirements

- Python 3.9 or above
- Telegram account
- Telegram API ID and API Hash
- Access to the required Telegram channel

---

## Installation

### 1. Create Virtual Environment

```bash
python -m venv venv
2. Activate Virtual Environment

Windows:

venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
Telegram API Setup
Visit:
https://my.telegram.org
Login using your Telegram account.
Open API Development Tools.
Create a new application.
Copy:
API ID
API Hash

Add these details in config.json.

Configuration

Example config.json:

{
    "api_id": "YOUR_API_ID",
    "api_hash": "YOUR_API_HASH",
    "channels": [
        "channel_name"
    ],
    "message_limit": 50,
    "image_folder": "images",
    "output_file": "deals.json",
    "log_file": "log.json"
}
Run the Project

Activate the virtual environment and run:

python telegram_deals_scraper.py

On the first run, Telegram will ask for the login verification code. After successful login, a session file will be created for future runs.

Output
deals.json

Stores scraped deal information:

Message ID
Date
Content
Product link
Image path
Channel name
images/

Contains downloaded product images from Telegram posts.

log.json

Stores scraper execution logs:

Successful connections
Scraped messages
Errors
Warning messages
Duplicate Handling

The scraper stores processed message IDs and checks them before saving new data. Already scraped messages are skipped to avoid duplicate entries.

Error Handling

The project handles:

Telegram FloodWaitError
Connection errors
JSON file errors
Unexpected exceptions
Security Notes
Keep api_id and api_hash private.
Do not share the Telegram session file.
Do not upload sensitive credentials to public repositories.