<<<<<<< Updated upstream
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


=======
# Telegram Deals Channel Scraper

A Python-based Telegram Deals Scraper that collects deal information from Telegram channels using the Telethon library, stores the scraped data in PostgreSQL, downloads product images, and provides Flask REST APIs for managing the deals.

## Project Overview

The project connects to Telegram using the Telegram MTProto API and a real Telegram user account. It reads messages from selected deal channels and extracts useful deal information such as:

- Telegram message ID
- Message date
- Deal content
- Product link
- Product image
- Channel name

The scraped data is stored in PostgreSQL and can also be maintained locally in JSON files.

The project also provides REST APIs using Flask for retrieving, updating, deleting, and scraping deals.

## Key Features

### Telegram Scraper

- Connects to Telegram using Telethon
- Uses Telegram MTProto API
- Scrapes messages from selected channels
- Configurable message limit
- Extracts product links from message content and buttons
- Downloads product images
- Prevents duplicate message processing
- Handles Telegram API rate limits using `FloodWaitError`
- Maintains scraper execution logs
- Saves scraped data locally in JSON files
- Stores scraped deals in PostgreSQL

### PostgreSQL Database

- PostgreSQL database integration
- Stores scraped deals permanently
- Stores scraper execution logs
- Unique constraint on Telegram message ID
- Prevents duplicate database records
- Supports CRUD operations
- Uses environment variables for database credentials

### Flask REST API

The project provides APIs for:

- Getting all deals
- Getting a single deal
- Updating a deal
- Deleting a deal
- Starting Telegram scraping
- Checking scraper status
- Pagination
- Channel filtering
- Request validation
- Background scraping

### Image Management

- Downloads images from Telegram messages
- Stores images inside the `images/` directory
- Saves image paths in PostgreSQL
- Automatically removes the associated image when a deal is deleted through the API

### Logging

The project maintains logs for:

- Successful connections
- Scraped messages
- Saved messages
- Duplicate messages
- Errors
- Warnings
- Telegram API errors
- Database errors
- Scraper execution status

Logs are maintained locally in `log.json` and database logs are stored in the PostgreSQL `logs` table.

## Technologies Used

- Python 3.9+
- Telethon
- Telegram MTProto API
- Flask
- PostgreSQL
- psycopg2
- python-dotenv
- REST API
- JSON
- Threading
- Async Programming
- Git & GitHub

## Project Structure

```text
scraping_python/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── images/
│   └── downloaded product images
│
├── telegram_deals_scraper.py   # Main Telegram scraper
├── database.py                  # PostgreSQL database operations
├── api.py                       # Flask REST API routes
├── app.py                       # Flask application entry point
├── gui.py                       # Desktop GUI
├── sync_json_to_db.py           # JSON to PostgreSQL synchronization
├── test_db.py                   # Database connection testing
│
├── config.json                  # Telegram scraper configuration
├── deals.json                   # Local scraped deal data
├── log.json                     # Local execution logs
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignored files
├── README.md                    # Project documentation
│
└── .env                         # Local environment variables
>>>>>>> Stashed changes
Requirements

Before running the project, install:

Python 3.9 or above
PostgreSQL
Telegram account
Telegram API ID
Telegram API Hash
Access to the required Telegram channels
Installation
<<<<<<< Updated upstream

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
=======
1. Clone the Repository
git clone https://github.com/aviralyadav-in/scraping_python.git
cd scraping_python
2. Create Virtual Environment
python -m venv venv
3. Activate Virtual Environment
Windows
venv\Scripts\activate
Linux / macOS
source venv/bin/activate
4. Install Dependencies
pip install -r requirements.txt
Telegram API Setup

The scraper uses Telegram's official API through Telethon.

Open:

https://my.telegram.org
>>>>>>> Stashed changes

Steps:

Login using your Telegram account.
Open API Development Tools.
Create a new application.
Obtain:
API ID
API Hash
Add the required values to your local configuration.

<<<<<<< Updated upstream
Add the required Telegram configuration to config.json.
=======
Keep the Telegram API credentials private.
>>>>>>> Stashed changes

Scraper Configuration

The scraper uses config.json for configuration.

Example:

<<<<<<< Updated upstream
Create the deals table:
=======
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
Configuration Fields
Field	Description
api_id	Telegram API ID
api_hash	Telegram API Hash
channels	Telegram channels to scrape
message_limit	Maximum messages to scrape
image_folder	Folder for downloaded images
output_file	Local deal JSON file
log_file	Local log JSON file
PostgreSQL Database Setup

Create a PostgreSQL database:

CREATE DATABASE telegram_deals;

Connect to the database and create the deals table:
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
Database credentials are stored in .env instead of being written directly in the source code.
=======
Database credentials are stored in a local .env file.
>>>>>>> Stashed changes

Create .env in the project root:

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

<<<<<<< Updated upstream
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

=======
The .gitignore should contain:

.env
venv/
__pycache__/
*.pyc
*.session
config.json
>>>>>>> Stashed changes
Running the Telegram Scraper

Activate the virtual environment:

venv\Scripts\activate

Run:

python telegram_deals_scraper.py

On the first run, Telethon may ask for:

Phone number
Telegram verification code
Two-factor authentication password, if enabled

After successful authentication, Telethon creates a session file that can be reused for future runs.

Running the Flask API

Start the Flask application:

python app.py

<<<<<<< Updated upstream
The APIs can be tested using Postman or a browser.

=======
The API can then be tested using:

Browser
Postman
Frontend application
>>>>>>> Stashed changes
REST API Endpoints
API 1 - Get All Deals
GET /api/deals/

Optional parameters:

channel
page
limit

Example:

GET /api/deals/?page=1&limit=10

<<<<<<< Updated upstream
Channel filtering:

GET /api/deals/?channel=channel_name&page=1&limit=10

Response contains:
=======
With channel filtering:

GET /api/deals/?channel=channel_name&page=1&limit=10

Example response:
>>>>>>> Stashed changes

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

Returns the details of a specific Telegram deal.

API 3 - Update Deal
POST /api/deals/<message_id>/update/

<<<<<<< Updated upstream
Example JSON:
=======
Example request body:
>>>>>>> Stashed changes

{
    "content": "Updated deal content",
    "product_link": "https://example.com/product",
    "image_path": "images/product.jpg"
}

<<<<<<< Updated upstream
The API validates the request body and allowed fields before updating the deal.
=======
The API validates the request body and allowed update fields.
>>>>>>> Stashed changes

API 4 - Delete Deal
DELETE /api/deals/<message_id>/

<<<<<<< Updated upstream
The API deletes the deal from PostgreSQL and also removes its associated image file when available.
=======
The API:
>>>>>>> Stashed changes

Finds the deal.
Deletes the database record.
Removes the associated image file if it exists.
API 5 - Start Telegram Scraping
POST /api/scrape/start/

<<<<<<< Updated upstream
Example:
=======
Example request body:
>>>>>>> Stashed changes

{
    "channel": "channel_name",
    "limit": 50
}

<<<<<<< Updated upstream
The scraper runs in a background thread, allowing the API to return immediately.
=======
The scraper runs in a background thread, allowing the API to return immediately without waiting for the scraping process to finish.
>>>>>>> Stashed changes

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

Possible scraper states include:

idle
running
completed
failed
API Validation

<<<<<<< Updated upstream
The APIs validate:
=======
The REST API validates:
>>>>>>> Stashed changes

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
Duplicate scraping requests

<<<<<<< Updated upstream
The API uses appropriate HTTP status codes such as:
=======
Common HTTP status codes:
>>>>>>> Stashed changes

Status Code	Meaning
200	Successful request
202	Request accepted / scraping started
400	Invalid request
404	Resource not found
409	Conflict
500	Internal server error
Pagination

The deals API supports pagination.

Example:

GET /api/deals/?page=1&limit=10

The response includes:

<<<<<<< Updated upstream
Total count
Current page
Result limit
Deal results
=======
{
    "count": 100,
    "page": 1,
    "limit": 10,
    "results": []
}

The API also supports channel-based filtering.

Example:

GET /api/deals/?channel=Allpackbypiyush&page=1&limit=10
>>>>>>> Stashed changes
Duplicate Handling

The scraper prevents duplicate message processing using Telegram message IDs.

<<<<<<< Updated upstream
The database also has a unique constraint on message_id.
=======
The database also has a unique constraint:
>>>>>>> Stashed changes

message_id BIGINT UNIQUE

<<<<<<< Updated upstream
ON CONFLICT (message_id) DO NOTHING;
=======
New records use conflict handling so that the same Telegram message is not inserted multiple times.
>>>>>>> Stashed changes

Conceptually:

ON CONFLICT (message_id) DO NOTHING;

This provides duplicate protection at both the scraper and database level.

Image Handling

<<<<<<< Updated upstream
When a Telegram message contains an image, the scraper downloads it into the images/ directory.

The image path is stored in PostgreSQL along with the deal information.

When a deal is deleted through the API, its associated image is also removed if the file exists.
=======
When a Telegram message contains an image:

The scraper detects the image.
The image is downloaded.
The image is stored inside the images/ directory.
The image path is saved in the database.
The image can be accessed through the deal information.
When the deal is deleted through the API, the associated image is also removed.
Error Handling

The project handles several types of errors, including:
>>>>>>> Stashed changes

Telegram connection errors
FloodWaitError
PostgreSQL connection errors
Database query errors
JSON file errors
Invalid API requests
Missing request data
Duplicate database records
File handling errors
Unexpected exceptions
Logging

<<<<<<< Updated upstream
The project maintains both local and database logs.

Local logs are stored in:

log.json

Database logs are stored in the PostgreSQL logs table.
=======
The scraper maintains execution logs.
>>>>>>> Stashed changes

Logs can include:

Telegram connection status
Scraping started
Messages scraped
Messages saved
Duplicate messages
Image download status
Database operations
Warnings
Errors
Telegram API errors
<<<<<<< Updated upstream
Database errors
Error Handling
=======
Scraping completion status

Local logs are stored in:

log.json

Database logs are stored in:

logs
>>>>>>> Stashed changes

PostgreSQL table.

<<<<<<< Updated upstream
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
=======
Security

Sensitive credentials are kept outside the source code.

The project uses environment variables for database credentials.

The following files must remain private:
>>>>>>> Stashed changes

.env
*.session
config.json

Do not expose:

Telegram API ID
Telegram API Hash
PostgreSQL password
<<<<<<< Updated upstream
Telegram session credentials

The .env file is excluded from Git using .gitignore.

Git and GitHub

The project is maintained using Git and GitHub.

Before pushing changes:
=======
Telegram session files
Database credentials

Never commit secrets to GitHub.

Git Workflow

Before committing changes:
>>>>>>> Stashed changes

git status

Stage required files:

git add .

Commit changes:

git commit -m "Update Telegram scraper project"

Push changes:

git push origin main

Check the configured remote:

git remote -v

The project repository is:

https://github.com/aviralyadav-in/scraping_python
Project Status

The project currently includes a complete Telegram deal scraping and management workflow:

<<<<<<< Updated upstream
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
=======
Telegram deal scraping
Product link extraction
Product image downloading
Duplicate message prevention
PostgreSQL database integration
Environment-based database configuration
Flask REST APIs
CRUD operations for deals
Background scraping
Scraper status tracking
Pagination
Channel filtering
API validation
Execution logging
JSON data storage
Desktop GUI
Frontend integration
Git/GitHub version control
Future Improvements

Possible future enhancements:

User authentication for APIs
API authorization
Advanced deal search
Multiple channel management
Scheduled automatic scraping
Better frontend dashboard
Docker deployment
Cloud database deployment
Production deployment
API documentation using Swagger/OpenAPI
>>>>>>> Stashed changes
