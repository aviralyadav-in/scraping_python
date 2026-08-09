Telegram Deals Channel Scraper

Project Description

Telegram Deals Channel Scraper is a Python automation project that connects to Telegram using the Telethon library and extracts deal information from Telegram deal channels.

The project collects deal information from Telegram messages and stores it in a PostgreSQL database. It also downloads product images and provides REST APIs using Flask to access and manage the scraped data.

The project includes:

Telegram message scraping
Product link extraction
Product image downloading
Duplicate message prevention
PostgreSQL database storage
Flask REST APIs
Scraper start and status APIs
CRUD operations for deals
Pagination and channel filtering
Environment variable based database configuration
Execution logging
Technologies Used
Python 3.9+
Telethon
Telegram MTProto API
Flask
PostgreSQL
psycopg2
python-dotenv
JSON
REST API
Threading
Async Programming
Features
Telegram Scraper
Connects to Telegram using a real user account
Scrapes messages from selected Telegram channels
Extracts product links from messages and buttons
Downloads attached product images
Prevents duplicate message scraping
Handles Telegram API rate limits using FloodWaitError
Maintains execution logs
Supports configurable message limits
PostgreSQL Database

Scraped deals are stored in PostgreSQL.

The deals table stores:

Message ID
Post date
Deal content
Product link
Image path
Channel name

The project also maintains a logs table for scraper execution logs.

Flask REST API

The project provides REST APIs for:

Getting all deals
Getting a single deal
Updating a deal
Deleting a deal
Starting Telegram scraping
Checking scraper status
Security

Database credentials are loaded using environment variables instead of storing the PostgreSQL password directly in the source code.

The .env file is excluded from Git using .gitignore.

Project Structure
TelegramScraper/
│
├── telegram_deals_scraper.py    # Main Telegram scraper
├── database.py                   # PostgreSQL database operations
├── api.py                       # Flask API routes
├── app.py                       # Flask application entry point
├── gui.py                       # Desktop GUI
│
├── config.json                  # Telegram scraper configuration
├── .env                         # Environment variables (not committed)
├── .gitignore                   # Git ignored files
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
│
├── deals.json                   # Local scraped deal data
├── log.json                     # Local execution logs
│
├── images/                      # Downloaded product images
│
├── session.session              # Telegram login session
│
└── venv/                        # Python virtual environment
Requirements

Before running the project, install:

Python 3.9 or above
PostgreSQL
Telegram account
Telegram API ID
Telegram API Hash
Access to the required Telegram channels
Installation
1. Clone the Repository
git clone https://github.com/arpita-1112/TelegramScraper.git
cd TelegramScraper
2. Create Virtual Environment
python -m venv venv
3. Activate Virtual Environment

Windows:

venv\Scripts\activate
4. Install Dependencies
pip install -r requirements.txt
Telegram API Setup

Open Telegram's API development page:

https://my.telegram.org

Login using your Telegram account.

Open:

API Development Tools

Create an application and obtain:

API ID
API Hash

Add these values to the project's configuration as required by the scraper.

Database Setup

Install PostgreSQL and create a database named:

telegram_deals

Create the required tables:

CREATE TABLE deals (
    id SERIAL PRIMARY KEY,
    message_id BIGINT UNIQUE,
    date TIMESTAMP,
    content TEXT,
    product_link TEXT,
    image_path TEXT,
    channel TEXT
);

Create the logs table:

CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    time TIMESTAMP,
    status TEXT,
    message TEXT
);
Environment Variables

Database credentials are stored in a .env file.

Create a .env file in the project root:

DB_HOST=localhost
DB_NAME=telegram_deals
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
DB_PORT=5432

The application loads these values using python-dotenv.

Example:

from dotenv import load_dotenv
import os

load_dotenv()

password = os.getenv("DB_PASSWORD")
Important

Do not upload .env to GitHub.

The .gitignore file should contain:

.env
venv/
__pycache__/
Scraper Configuration

The Telegram scraper uses a configuration file for settings such as:

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

Keep sensitive Telegram credentials private.

Running the Scraper

Activate the virtual environment:

venv\Scripts\activate

Run the scraper:

python telegram_deals_scraper.py

On the first run, Telegram may ask for the login verification code.

After successful authentication, Telethon creates a session file that can be reused for future runs.

Running the Flask API

The Flask application can be started using the project entry point:

python app.py

The API runs locally and can be tested using a browser or Postman.

API Endpoints
API 1 - Get All Deals
GET /api/deals/

Optional query parameters:

channel
page
limit

Example:

GET /api/deals/?page=1&limit=3

Example with channel filtering:

GET /api/deals/?channel=channel_name&page=1&limit=10
API 2 - Get Single Deal
GET /api/deals/<message_id>/

Example:

GET /api/deals/78021/
API 3 - Update Deal
POST /api/deals/<message_id>/update/

Example JSON body:

{
    "content": "Updated deal content",
    "product_link": "https://example.com/product",
    "image_path": "images/product.jpg"
}
API 4 - Delete Deal
DELETE /api/deals/<message_id>/

The API also removes the associated image file when it exists.

API 5 - Start Telegram Scraping
POST /api/scrape/start/

Example JSON body:

{
    "channel": "channel_name",
    "limit": 50
}

The scraper runs in a background thread so that the API can immediately return a response.

API 6 - Scraping Status
GET /api/scrape/status/

The response provides information such as:

Scraper status
Channel
Start time
Completion time
Messages scraped
Messages saved
Error information

Example response:

{
    "status": "completed",
    "channel": "channel_name",
    "started_at": "2026-08-09 12:00:00",
    "completed_at": "2026-08-09 12:01:30",
    "messages_scraped": 50,
    "messages_saved": 45,
    "error": null
}
API Validation

The API validates:

Page number
Result limit
Message ID
Channel name
JSON request body
Required fields
Allowed update fields
Data types
Empty values
Scraper status

The API returns appropriate HTTP status codes such as:

200 OK
202 Accepted
400 Bad Request
404 Not Found
409 Conflict
500 Internal Server Error
Pagination

The deals API supports pagination.

Example:

GET /api/deals/?page=1&limit=10

The response contains:

{
    "count": 100,
    "page": 1,
    "limit": 10,
    "results": []
}
Duplicate Handling

The scraper prevents duplicate message processing by checking previously processed message IDs.

The database also uses a unique constraint on message_id.

New records use:

ON CONFLICT (message_id)
DO NOTHING;

This prevents the same Telegram message from being inserted multiple times.

Image Handling

When a Telegram post contains an image, the scraper downloads it into the images/ directory.

The database stores the image path along with the deal.

When a deal is deleted through the API, the associated image file is also removed if it exists.

Logging

The project maintains execution logs.

Logs can contain:

Successful connections
Scraped messages
Saved messages
Duplicate messages
Errors
Warning messages
Telegram API errors

Local logs are stored in:

log.json

Database logs are stored in the PostgreSQL logs table.

Error Handling

The project handles:

FloodWaitError
Telegram connection errors
PostgreSQL connection errors
JSON file errors
Invalid API requests
Duplicate database records
Unexpected exceptions
Security Notes

Never commit sensitive credentials to GitHub.

Do not upload:

.env
session.session

Do not expose:

Telegram API ID
Telegram API Hash
PostgreSQL password
Telegram session files

The .env file should remain local and should be included in .gitignore.

Git

Before pushing changes to GitHub, check:

git status

Stage only the required project files:

git add database.py api.py app.py .gitignore README.md

Commit:

git commit -m "Update API and secure database configuration"

Push:

git push origin main
Project Status

The project currently includes:

Telegram deal scraping
Product image downloading
Duplicate handling
PostgreSQL database integration
Environment variable based database credentials
Flask REST APIs
Background scraping
Scraper status tracking
CRUD operations
API validation
Pagination
Logging
Git/GitHub version control
