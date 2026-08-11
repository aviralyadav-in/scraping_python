from flask import jsonify, request, send_from_directory
from flask_cors import CORS

from database import (
    get_connection,
    get_deals,
    get_deal,
    count_deals,
    update_deal,
    delete_deal,
    get_logs
)

from telegram_deals_scraper import start_scraper

import threading
import re
import os
from datetime import datetime, timezone


scraper_status = {
    "status": "idle",
    "channel": None,
    "limit": 0,
    "started_at": None,
    "completed_at": None,
    "messages_scraped": 0,
    "messages_saved": 0,
    "current_deal": None,
    "error": None,
    "stop_requested": False
}

scraper_lock = threading.Lock()
stop_event = threading.Event()


def register_routes(app):

    CORS(app)

    @app.route("/")
    def home():

        return jsonify({
            "message": "Telegram Deals API is running"
        }), 200

    @app.route("/images/<path:filename>", methods=["GET"])
    def serve_image(filename):

        image_folder = os.path.join(
            os.getcwd(),
            "images"
        )

        return send_from_directory(
            image_folder,
            filename
        )
    
    @app.route("/api/deals/", methods=["GET"])
    def get_all_deals():

        channel = request.args.get("channel")
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")

        page = request.args.get("page", "1")
        limit = request.args.get("limit", "10")

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

        if from_date:

            try:
                datetime.strptime(
                    from_date,
                    "%Y-%m-%d"
                )
            except ValueError:
                return jsonify({
                    "error": "from_date must be in YYYY-MM-DD format"
                }), 400

        if to_date:

            try:
                datetime.strptime(
                    to_date,
                    "%Y-%m-%d"
                )
            except ValueError:
                return jsonify({
                    "error": "to_date must be in YYYY-MM-DD format"
                }), 400

        if from_date and to_date:

            if from_date > to_date:
                return jsonify({
                    "error": "from_date cannot be greater than to_date"
                }), 400

        try:

            deals = get_deals(
                channel=channel,
                from_date=from_date,
                to_date=to_date,
                page=page,
                limit=limit
            )

            total_count = count_deals(
                channel=channel,
                from_date=from_date,
                to_date=to_date
            )

            return jsonify({
                "count": total_count,
                "page": page,
                "limit": limit,
                "channel": channel,
                "from_date": from_date,
                "to_date": to_date,
                "results": deals
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    @app.route(
        "/api/deals/<message_id>/",
        methods=["GET"]
    )
    def get_single_deal(message_id):

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

        channel = request.args.get("channel")

        if not channel:
            return jsonify({
                "error": "Channel is required"
            }), 400

        try:

            deal = get_deal(
                message_id,
                channel
            )

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


    @app.route(
        "/api/deals/<message_id>/update/",
        methods=["POST"]
    )
    def update_single_deal(message_id):

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

        channel = request.args.get("channel")

        if not channel:
            return jsonify({
                "error": "Channel is required"
            }), 400

        if not request.is_json:
            return jsonify({
                "error": "Request body must be JSON"
            }), 400

        data = request.get_json()

        if not isinstance(data, dict):
            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        if not data:
            return jsonify({
                "error": "Request body cannot be empty"
            }), 400

        allowed_fields = {
            "content",
            "product_link",
            "image_path"
        }

        invalid_fields = set(data.keys()) - allowed_fields

        if invalid_fields:
            return jsonify({
                "error": "Invalid field(s)",
                "fields": list(invalid_fields)
            }), 400

        if "content" in data:

            if not isinstance(data["content"], str):
                return jsonify({
                    "error": "content must be a string"
                }), 400

            if not data["content"].strip():
                return jsonify({
                    "error": "content cannot be empty"
                }), 400

        if "product_link" in data:

            if not isinstance(data["product_link"], str):
                return jsonify({
                    "error": "product_link must be a string"
                }), 400

            if not data["product_link"].strip():
                return jsonify({
                    "error": "product_link cannot be empty"
                }), 400

        if "image_path" in data:

            if not isinstance(data["image_path"], str):
                return jsonify({
                    "error": "image_path must be a string"
                }), 400

        try:

            deal = get_deal(
                message_id,
                channel
            )

            if deal is None:
                return jsonify({
                    "error": "Deal not found"
                }), 404

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

            updated_deal = update_deal(
                message_id=message_id,
                channel=channel,
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


    @app.route(
        "/api/deals/<message_id>/",
        methods=["DELETE"]
    )
    def delete_single_deal(message_id):

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

        channel = request.args.get("channel")

        if not channel:
            return jsonify({
                "error": "Channel is required"
            }), 400

        try:

            deleted_deal = delete_deal(
                message_id,
                channel
            )

            if deleted_deal is None:
                return jsonify({
                    "error": "Deal not found"
                }), 404

            image_path = deleted_deal.get(
                "image_path"
            )

            if image_path:

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


    def run_scraper_background(channel, limit):

        global scraper_status

        try:

            with scraper_lock:

                stop_event.clear()

                scraper_status["status"] = "running"
                scraper_status["channel"] = channel
                scraper_status["limit"] = limit

                scraper_status["started_at"] = (
                    datetime.now(
                        timezone.utc
                    ).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                scraper_status["completed_at"] = None
                scraper_status["messages_scraped"] = 0
                scraper_status["messages_saved"] = 0
                scraper_status["current_deal"] = None
                scraper_status["error"] = None
                scraper_status["stop_requested"] = False

            print(
                f"SCRAPER STARTED: {channel}, LIMIT: {limit}"
            )

            result = start_scraper(
                channel_name=channel,
                limit=limit,
                stop_event=stop_event
            )

            if result is None:
                result = {}

            with scraper_lock:

                if scraper_status["stop_requested"]:
                    scraper_status["status"] = "stopped"
                else:
                    scraper_status["status"] = "completed"

                scraper_status["messages_scraped"] = result.get(
                    "messages_scraped",
                    0
                )

                scraper_status["messages_saved"] = result.get(
                    "messages_saved",
                    0
                )

                scraper_status["current_deal"] = result.get(
                    "current_deal"
                )

                scraper_status["completed_at"] = (
                    datetime.now(
                        timezone.utc
                    ).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

            print("SCRAPER FINISHED")

        except Exception as e:

            print("SCRAPER ERROR:", str(e))

            with scraper_lock:

                scraper_status["status"] = "failed"
                scraper_status["error"] = str(e)

                scraper_status["completed_at"] = (
                    datetime.now(
                        timezone.utc
                    ).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )


    @app.route(
        "/api/scrape/start/",
        methods=["POST"]
    )
    def start_scraping():

        if not request.is_json:
            return jsonify({
                "error": "Request body must be JSON"
            }), 400

        data = request.get_json()

        if not isinstance(data, dict):
            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        channel = data.get("channel")

        if channel is None:
            return jsonify({
                "error": "Channel is required"
            }), 400

        if not isinstance(channel, str):
            return jsonify({
                "error": "Channel must be a string"
            }), 400

        channel = channel.strip()
        channel = channel.lower()

        if not channel:
            return jsonify({
                "error": "Channel cannot be empty"
            }), 400

        if not re.fullmatch(
            r"[A-Za-z_][A-Za-z_]{4,31}",
            channel
        ):
            return jsonify({
                "error": "Invalid channel name. Use 5-32 letters or underscores."
            }), 400

        limit = data.get(
            "limit",
            100
        )

        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
        ):
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

        with scraper_lock:

            if scraper_status["status"] == "running":

                return jsonify({
                    "error": "Scraper is already running",
                    "channel": scraper_status["channel"]
                }), 409

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


    @app.route(
        "/api/scrape/stop/",
        methods=["POST"]
    )
    def stop_scraping():

        with scraper_lock:

            if scraper_status["status"] != "running":

                return jsonify({
                    "error": "Scraper is not running",
                    "status": scraper_status["status"]
                }), 409

            scraper_status["stop_requested"] = True

            stop_event.set()

        return jsonify({
            "message": "Stop request received",
            "status": "stopping"
        }), 202


    @app.route(
        "/api/scrape/status/",
        methods=["GET"]
    )
    def scraping_status():

        with scraper_lock:

            return jsonify({
                "status": scraper_status["status"],
                "channel": scraper_status["channel"],
                "limit": scraper_status["limit"],
                "started_at": scraper_status["started_at"],
                "completed_at": scraper_status["completed_at"],
                "messages_scraped": scraper_status["messages_scraped"],
                "messages_saved": scraper_status["messages_saved"],
                "current_deal": scraper_status["current_deal"],
                "error": scraper_status["error"],
                "stop_requested": scraper_status["stop_requested"]
            }), 200


    @app.route("/api/logs/",methods=["GET"])
    def get_all_logs():
        page = request.args.get(
            "page",
            "1"
        )

        limit = request.args.get(
            "limit",
            "10"
        )

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

        try:
            limit = int(limit)
        except ValueError:
            return jsonify({
                "error": "Limit must be a number"
            }), 400

        if limit < 1:
            return jsonify({
                "error": "Limit must be greater than 0"
            }), 400

        if limit > 500:
            return jsonify({
                "error": "Limit cannot be greater than 500"
            }), 400

        try:

            logs = get_logs(
                page=page,
                limit=limit
            )

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM logs;
                """
            )

            total_count = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            return jsonify({
                "count": total_count,
                "page": page,
                "limit": limit,
                "results": logs
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500
        