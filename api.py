from flask import Flask, jsonify, request
from database import get_deals, get_deal, count_deals, update_deal, delete_deal
from telegram_deals_scraper import start_scraper
import threading
import re
from datetime import datetime, timezone

app = Flask(__name__)

# Scraper status
scraper_status = {
    "status": "idle",
    "channel": None,
    "started_at": None,
    "completed_at": None,
    "messages_scraped": 0,
    "messages_saved": 0,
    "error": None
}

scraper_lock = threading.Lock()

# Home

@app.route("/")
def home():

    return jsonify({
        "message": "Telegram Deals API is running"
    })


# API 1 - Get All Deals

@app.route("/api/deals/", methods=["GET"])
def get_all_deals():

    # Get query parameters
    channel = request.args.get("channel")
    page = request.args.get("page", "1")
    limit = request.args.get("limit", "3")

    # Validate page
    try:
        page = int(page)

    except ValueError:

        return jsonify({
            "error": "Page must be a number"
        }), 400

    if page < 1:

        return jsonify({
            "error": "Page must be greater than or equal to 1"
        }), 400

    # Validate limit
    try:
        limit = int(limit)

    except ValueError:

        return jsonify({
            "error": "Limit must be a number"
        }), 400

    if limit < 1:

        return jsonify({
            "error": "Limit must be greater than or equal to 1"
        }), 400

    if limit > 100:

        return jsonify({
            "error": "Limit cannot be greater than 100"
        }), 400

    # Get deals from database
    try:

        deals = get_deals(
            channel=channel,
            page=page,
            limit=limit
        )
        total_count = count_deals(
                channel=channel
        )
        return jsonify({
            "count": total_count,
            "page": page,
            "limit": limit,
            "results": deals
        }), 200

    except Exception as e:

        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500


# API 2 - Get Single Deal

@app.route("/api/deals/<message_id>/", methods=["GET"])
def get_single_deal(message_id):

    # Validate message_id
    try:

        message_id = int(message_id)

    except ValueError:

        return jsonify({
            "error": "message_id must be an integer"
        }), 400

    # Get deal from database
    try:

        deal = get_deal(message_id)

        if deal is None:

            return jsonify({
                "error": "Deal not found"
            }), 404

        return jsonify(deal), 200

    except Exception as e:

        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500


# API 3 - Update Deal

@app.route("/api/deals/<message_id>/update/", methods=["POST"])
def update_single_deal(message_id):

    # Validate message_id
    try:

        message_id = int(message_id)

    except ValueError:

        return jsonify({
            "error": "message_id must be an integer"
        }), 400

    if message_id < 1:

        return jsonify({
            "error": "message_id must be greater than 0"
        }), 400

    # Check JSON body
    if not request.is_json:

        return jsonify({
            "error": "Request body must be JSON"
        }), 400

    data = request.get_json()

    # Check request body
    if not isinstance(data, dict):

        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    # Check empty body
    if not data:

        return jsonify({
            "error": "Request body cannot be empty"
        }), 400

    # Allowed fields
    allowed_fields = {
        "content",
        "product_link",
        "image_path"
    }

    # Check invalid fields
    invalid_fields = set(data.keys()) - allowed_fields

    if invalid_fields:

        return jsonify({
            "error": "Invalid field(s)",
            "fields": list(invalid_fields)
        }), 400

    # Validate content if provided
    if "content" in data:

        if not isinstance(data["content"], str):

            return jsonify({
                "error": "content must be a string"
            }), 400

        if not data["content"].strip():

            return jsonify({
                "error": "content cannot be empty"
            }), 400

    # Validate product_link if provided
    if "product_link" in data:

        if not isinstance(data["product_link"], str):

            return jsonify({
                "error": "product_link must be a string"
            }), 400

        if not data["product_link"].strip():

            return jsonify({
                "error": "product_link cannot be empty"
            }), 400

    # Validate image_path if provided
    if "image_path" in data:

        if not isinstance(data["image_path"], str):

            return jsonify({
                "error": "image_path must be a string"
            }), 400

    # Check whether deal exists
    try:

        deal = get_deal(message_id)

        if deal is None:

            return jsonify({
                "error": "Deal not found"
            }), 404

        # Keep existing values if not provided
        content = data.get(
            "content",
            deal["content"]
        )

        product_link = data.get(
            "product_link",
            deal["product_link"]
        )

        image_path = data.get(
            "image_path",
            deal["image_path"]
        )

        # Update deal
        updated_deal = update_deal(
            message_id=message_id,
            content=content.strip(),
            product_link=product_link.strip(),
            image_path=image_path.strip()
        )

        return jsonify({
            "message": "Deal updated successfully",
            "data": updated_deal
        }), 200

    except Exception as e:

        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500

    # API 4 - Delete Deal

@app.route("/api/deals/<message_id>/", methods=["DELETE"])
def delete_single_deal(message_id):

    # Validate message_id
    try:

        message_id = int(message_id)

    except ValueError:

        return jsonify({
            "error": "message_id must be an integer"
        }), 400

    if message_id < 1:

        return jsonify({
            "error": "message_id must be greater than 0"
        }), 400

    # Delete deal from database
    try:

        deleted_deal = delete_deal(message_id)

        # Deal does not exist
        if deleted_deal is None:

            return jsonify({
                "error": "Deal not found"
            }), 404

        # Get image path
        image_path = deleted_deal.get("image_path")

        # Delete image file if it exists
        if image_path:

            import os

            if os.path.exists(image_path):

                os.remove(image_path)

        return jsonify({
            "message": "Deal deleted successfully"
        }), 200

    except Exception as e:

        return jsonify({
            "error": "Database error",
            "message": str(e)
        }), 500

    # Background scraper function

def run_scraper_background(channel, limit):

    global scraper_status

    try:

        with scraper_lock:

            scraper_status["status"] = "running"
            scraper_status["channel"] = channel
            scraper_status["started_at"] = datetime.now(
                timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S")

            scraper_status["completed_at"] = None
            scraper_status["messages_scraped"] = 0
            scraper_status["messages_saved"] = 0
            scraper_status["error"] = None

        # Run existing Telegram scraper
        result = start_scraper(
            channel_name=channel,
            limit=limit
        )

        with scraper_lock:
            scraper_status["messages_scraped"] = result.get(
        "messages_scraped",0)

            scraper_status["messages_saved"] = result.get(
        "messages_saved",0 )
            
            scraper_status["status"] = "completed"
            scraper_status["completed_at"] = datetime.now(
                timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:

        with scraper_lock:

            scraper_status["status"] = "failed"
            scraper_status["error"] = str(e)

            # API 5 - Start Telegram Scraping

@app.route("/api/scrape/start/", methods=["POST"])
def start_scraping():

    global scraper_status

    # Check JSON body
    if not request.is_json:

        return jsonify({
            "error": "Request body must be JSON"
        }), 400

    data = request.get_json()

    # Check request body
    if not isinstance(data, dict):

        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    # Check channel
    if "channel" not in data:

        return jsonify({
            "error": "Channel is required"
        }), 400

    channel = data.get("channel")

    # Validate channel type
    if not isinstance(channel, str):

        return jsonify({
            "error": "Channel must be a string"
        }), 400

    channel = channel.strip()

    # Check empty channel
    if not channel:

        return jsonify({
            "error": "Channel cannot be empty"
        }), 400

    # Validate channel name
    if not re.fullmatch(
        r"[A-Za-z_][A-Za-z0-9_]{4,31}",
        channel
    ):

        return jsonify({
            "error": "Invalid channel name"
        }), 400

    # Get limit
    limit = data.get("limit", 100)

    # Validate limit
    if not isinstance(limit, int) or isinstance(limit, bool):

        return jsonify({
            "error": "Limit must be an integer"
        }), 400

    if limit < 1:

        return jsonify({
            "error": "Limit must be greater than or equal to 1"
        }), 400

    if limit > 100:

        return jsonify({
            "error": "Limit cannot be greater than 100"
        }), 400

    # Check whether scraper is already running
    with scraper_lock:

        if scraper_status["status"] == "running":

            return jsonify({
                "error": "Scraper is already running",
                "channel": scraper_status["channel"]
            }), 409

    # Start scraper in background
    scraper_thread = threading.Thread(
        target=run_scraper_background,
        args=(channel, limit),
        daemon=True
    )

    scraper_thread.start()

    return jsonify({
        "message": "Scraping started successfully",
        "channel": channel,
        "limit": limit
    }), 202

# API 6 - Scraping Status

@app.route("/api/scrape/status/", methods=["GET"])
def scraping_status():

    with scraper_lock:

        return jsonify({
            "status": scraper_status["status"],
            "channel": scraper_status["channel"],
            "started_at": scraper_status["started_at"],
            "completed_at": scraper_status["completed_at"],
            "messages_scraped": scraper_status["messages_scraped"],
            "messages_saved": scraper_status["messages_saved"],
            "error": scraper_status["error"]
        }), 200
    
    # Run Flask

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
