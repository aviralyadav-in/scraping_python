Project Description
Telegram Deals Channel Scraper is a Python automation project that connects to Telegram using the Telethon library and extracts deal information from Telegram deal channels.

The project scrapes Telegram messages, extracts product links, downloads product images, stores deal data in PostgreSQL, and provides Flask REST APIs to access and manage the scraped deals.

The project also includes a desktop GUI, pagination, channel filtering, duplicate prevention, execution logging, background scraping, and scraper status tracking.

Features
Telegram channel message scraping
Product link extraction from messages and Telegram buttons
Product image downloading
PostgreSQL database integration
Duplicate message prevention
Configurable message scraping limit
Telegram FloodWaitError handling
Execution logging
Flask REST APIs
CRUD operations for deals
Pagination
Channel filtering
Background scraping using threading
Scraper status tracking
API request validation
Environment variable based database configuration
Desktop GUI for scraper execution
JSON data and log generation
Git/GitHub version control
Technologies Used
Python 3.9+
Telethon
Flask
PostgreSQL
psycopg2
python-dotenv
REST API
JSON
Threading
Async Programming
CustomTkinter
HTML/CSS/JavaScript
React.js
Postman
Git & GitHub
Project Structure
scraping_python/
│
├── telegram_deals_scraper.py   # Main Telegram scraper
├── database.py                 # PostgreSQL database operations
├── api.py                      # Flask API routes
├── app.py                      # Flask application entry point
├── gui.py                      # Desktop GUI
├── sync_json_to_db.py          # JSON to PostgreSQL synchronization
├── test_db.py                  # Database connection testing
│
├── frontend/                   # Frontend application
├── images/                     # Downloaded product images
│
├── config.json                 # Telegram scraper configuration
├── .env                        # Database environment variables
├── .gitignore                  # Git ignored files
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── deals.json                  # Local scraped deal data
├── log.json                    # Local execution logs
│
├── session.session             # Telegram session file
└── venv/                       # Python virtual environment


Requirements

Before running the project, install:

Python 3.9 or above
PostgreSQL
Telegram account
Telegram API ID
Telegram API Hash
Access to the required Telegram channels
Installation

Clone the repository:

git clone https://github.com/aviralyadav-in/scraping_python.git
cd scraping_python

Create a virtual environment:

python -m venv venv

Activate the virtual environment on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt
Telegram API Setup

Open:

https://my.telegram.org

Login using your Telegram account and open API Development Tools.

Create an application and obtain:

API ID
API Hash

Add the required Telegram configuration to config.json.

Database Setup

Install PostgreSQL and create a database named:

telegram_deals

Create the deals table:

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

Database credentials are stored in .env instead of being written directly in the source code.

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

Never upload .env to GitHub.

Scraper Configuration

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

Keep Telegram API credentials private.

Running the Telegram Scraper

Activate the virtual environment:

venv\Scripts\activate

Run:

python telegram_deals_scraper.py

On the first run, Telegram may ask for the login verification code.

After successful authentication, Telethon creates a session file that can be reused for future runs.

Running the Flask API

Start the Flask application:

python app.py

The APIs can be tested using Postman or a browser.

REST API Endpoints
API 1 - Get All Deals
GET /api/deals/

Optional parameters:

channel
page
limit

Example:

GET /api/deals/?page=1&limit=10

Channel filtering:

GET /api/deals/?channel=channel_name&page=1&limit=10

Response contains:

{
    "count": 100,
    "page": 1,
    "limit": 10,
    "results": []
}
API 2 - Get Single Deal
GET /api/deals/<message_id>/

Example:

GET /api/deals/78021/
API 3 - Update Deal
POST /api/deals/<message_id>/update/

Example JSON:

{
    "content": "Updated deal content",
    "product_link": "https://example.com/product",
    "image_path": "images/product.jpg"
}

The API validates the request body and allowed fields before updating the deal.

API 4 - Delete Deal
DELETE /api/deals/<message_id>/

The API deletes the deal from PostgreSQL and also removes its associated image file when available.

API 5 - Start Telegram Scraping
POST /api/scrape/start/

Example:

{
    "channel": "channel_name",
    "limit": 50
}

The scraper runs in a background thread, allowing the API to return immediately.

API 6 - Scraper Status
GET /api/scrape/status/

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

The APIs validate:

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

The API uses appropriate HTTP status codes such as:

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

The response includes:

Total count
Current page
Result limit
Deal results
Duplicate Handling

The scraper prevents duplicate message processing using Telegram message IDs.

The database also has a unique constraint on message_id.

New records use:

ON CONFLICT (message_id) DO NOTHING;

This prevents the same Telegram message from being inserted multiple times.

Image Handling

When a Telegram message contains an image, the scraper downloads it into the images/ directory.

The image path is stored in PostgreSQL along with the deal information.

When a deal is deleted through the API, its associated image is also removed if the file exists.

Logging

The project maintains both local and database logs.

Local logs are stored in:

log.json

Database logs are stored in the PostgreSQL logs table.

Logs can contain:

Successful connections
Scraped messages
Saved messages
Duplicate messages
Errors
Warning messages
Telegram API errors
Database errors
Error Handling

The project handles:

Telegram connection errors
FloodWaitError
PostgreSQL connection errors
JSON file errors
Invalid API requests
Duplicate database records
Missing data
Unexpected exceptions
Security

Sensitive credentials are not stored directly in the source code.

The following files should remain private:

.env
session.session

Do not expose:

Telegram API ID
Telegram API Hash
PostgreSQL password
Telegram session credentials

The .env file is excluded from Git using .gitignore.

Git and GitHub

The project is maintained using Git and GitHub.

Before pushing changes:

git status

Stage required files:

git add .

Commit changes:

git commit -m "Update Telegram scraper project"

Push changes:

git push origin main
Project Status

The project currently includes a complete Telegram deal scraping and management workflow:

Telegram message scraping
Product link extraction
Product image downloading
Duplicate prevention
PostgreSQL database integration
Environment-based database credentials
Flask REST APIs
Get, update and delete deal operations
Pagination and channel filtering
Background scraping
Scraper status tracking
API validation
Execution logging
Desktop GUI
Frontend integration
JSON and database synchronization
Git/GitHub version control

The project is ready for further development and deployment.
