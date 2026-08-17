from flask import jsonify, request, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets
from flask_cors import CORS

from database import (
    get_connection,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_all_users,
    get_deals,
    get_deal,
    count_deals,
    update_deal,
    delete_deal,
    get_logs,
    bulk_update_deals,
    bulk_delete_deals,
    get_deal_status,
    update_deal_status,
    get_duplicate_deals,
    get_deal_statistics,
    create_scraping_job,
    get_scraping_job,
    update_scraping_job,
    get_scraping_jobs,
    count_scraping_jobs,
    create_retry_job,
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
    sessions = {}

    def get_current_user():
        token = request.headers.get("Authorization")

        if not token:
            return None

        if token.startswith("Bearer "):
            token = token[7:]

        user_id = sessions.get(token)

        if not user_id:
            return None

        return get_user_by_id(user_id)


    def login_required(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            user = get_current_user()

            if user is None:
                return jsonify({
                    "error": "Authentication required"
                }), 401

            return f(*args, **kwargs)

        return decorated_function


    def admin_required(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            user = get_current_user()

            if user is None:
                return jsonify({
                    "error": "Authentication required"
                }), 401

            if user["role"] != "admin":
                return jsonify({
                    "error": "Admin access required"
                }), 403

            return f(*args, **kwargs)

        return decorated_function
    
    @app.route(
        "/api/auth/login/",
        methods=["POST"]
    )
    def login():

        if not request.is_json:
            return jsonify({
                "error": "Request body must be JSON"
            }), 400

        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "error": "Email and password are required"
            }), 400

        user = get_user_by_email(email.strip().lower())

        if user is None:
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        if not check_password_hash(
            user["password_hash"],
            password
        ):
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        token = secrets.token_urlsafe(32)

        sessions[token] = user["id"]

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200

    @app.route(
        "/api/auth/logout/",
        methods=["POST"]
    )
    def logout():

        token = request.headers.get("Authorization")

        if token and token.startswith("Bearer "):
            token = token[7:]

        if token:
            sessions.pop(token, None)

        return jsonify({
            "message": "Logout successful"
        }), 200

    @app.route(
        "/api/auth/me/",
        methods=["GET"]
    )
    @login_required
    def current_user():

        user = get_current_user()

        return jsonify({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }), 200

    @app.route(
        "/api/profile/",
        methods=["PUT"]
    )
    @login_required
    def update_my_profile():

        user = get_current_user()

        if not request.is_json:
            return jsonify({
                "error": "Request body must be JSON"
            }), 400

        data = request.get_json()

        if not isinstance(data, dict):
            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        name = data.get("name")
        email = data.get("email")

        if name is None and email is None:
            return jsonify({
                "error": "At least name or email is required"
            }), 400

        if name is not None:

            if not isinstance(name, str):
                return jsonify({
                    "error": "Name must be a string"
                }), 400

            name = name.strip()

            if not name:
                return jsonify({
                    "error": "Name cannot be empty"
                }), 400

        if email is not None:

            if not isinstance(email, str):
                return jsonify({
                    "error": "Email must be a string"
                }), 400

            email = email.strip().lower()

            if not email:
                return jsonify({
                    "error": "Email cannot be empty"
                }), 400

            existing_user = get_user_by_email(email)

            if existing_user and existing_user["id"] != user["id"]:
                return jsonify({
                    "error": "Email is already registered"
                }), 409

        try:

            conn = get_connection()
            cursor = conn.cursor()

            if name is not None and email is not None:

                cursor.execute(
                    """
                    UPDATE users
                    SET name = %s,
                        email = %s
                    WHERE id = %s
                    RETURNING id, name, email, role;
                    """,
                    (name, email, user["id"])
                )

            elif name is not None:

                cursor.execute(
                    """
                    UPDATE users
                    SET name = %s
                    WHERE id = %s
                    RETURNING id, name, email, role;
                    """,
                    (name, user["id"])
                )

            else:

                cursor.execute(
                    """
                    UPDATE users
                    SET email = %s
                    WHERE id = %s
                    RETURNING id, name, email, role;
                    """,
                    (email, user["id"])
                )

            updated_user = cursor.fetchone()

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "message": "Profile updated successfully",
                "user": {
                    "id": updated_user[0],
                    "name": updated_user[1],
                    "email": updated_user[2],
                    "role": updated_user[3]
                }
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    @app.route(
        "/api/auth/change-password/",
        methods=["POST"]
    )
    @login_required
    def change_password():

        user = get_current_user()

        if not request.is_json:
            return jsonify({
                "error": "Request body must be JSON"
            }), 400

        data = request.get_json()

        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password:
            return jsonify({
                "error": "Current password is required"
            }), 400

        if not new_password:
            return jsonify({
                "error": "New password is required"
            }), 400

        if len(new_password) < 6:
            return jsonify({
                "error": "New password must contain at least 6 characters"
            }), 400

        if not check_password_hash(
            user["password_hash"],
            current_password
        ):
            return jsonify({
                "error": "Current password is incorrect"
            }), 401

        try:

            new_password_hash = generate_password_hash(
                new_password
            )

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE users
                SET password_hash = %s
                WHERE id = %s
                """,
                (new_password_hash, user["id"])
            )

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "message": "Password changed successfully"
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500

    @app.route(
        "/api/users/",
        methods=["POST"]
    )
    @admin_required
    def create_new_user():

        if not request.is_json:
            return jsonify({
                "error": "Request body must be JSON"
            }), 400

        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name:
            return jsonify({
                "error": "Name is required"
            }), 400

        if not email:
            return jsonify({
                "error": "Email is required"
            }), 400

        if not password:
            return jsonify({
                "error": "Password is required"
            }), 400

        name = name.strip()
        email = email.strip().lower()

        if len(password) < 6:
            return jsonify({
                "error": "Password must contain at least 6 characters"
            }), 400

        existing_user = get_user_by_email(email)

        if existing_user:
            return jsonify({
                "error": "User with this email already exists"
            }), 409

        hashed_password = generate_password_hash(
            password
        )

        try:

            user = create_user(
                name=name,
                email=email,
                password_hash=hashed_password,
                role="user"
            )

            return jsonify({
                "message": "User created successfully",
                "user": user
            }), 201

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500

    @app.route(
    "/api/users/",
    methods=["GET"]
    )
    @admin_required
    def get_users():

        try:

            users = get_all_users()

            return jsonify({
                "count": len(users),
                "results": users
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500
        
    @app.route(
    "/api/users/<user_id>/",
    methods=["PUT"]
)
    @admin_required
    def update_user(user_id):

        try:
            user_id = int(user_id)

        except ValueError:

            return jsonify({
                "error": "user_id must be an integer"
            }), 400

        if user_id < 1:

            return jsonify({
                "error": "user_id must be greater than 0"
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

        name = data.get("name")
        role = data.get("role")

        if name is None and role is None:

            return jsonify({
                "error": "At least name or role is required"
            }), 400

        if name is not None:

            if not isinstance(name, str):

                return jsonify({
                    "error": "name must be a string"
                }), 400

            name = name.strip()

            if not name:

                return jsonify({
                    "error": "name cannot be empty"
                }), 400

        if role is not None:

            if not isinstance(role, str):

                return jsonify({
                    "error": "role must be a string"
                }), 400

            role = role.strip().lower()

            if role not in {"admin", "user"}:

                return jsonify({
                    "error": "Invalid role. Use admin or user."
                }), 400

        user = get_user_by_id(user_id)

        if user is None:

            return jsonify({
                "error": "User not found"
            }), 404

        try:

            conn = get_connection()
            cursor = conn.cursor()

            if name is not None and role is not None:

                cursor.execute(
                    """
                    UPDATE users
                    SET name = %s,
                        role = %s
                    WHERE id = %s
                    RETURNING id, name, email, role;
                    """,
                    (name, role, user_id)
                )

            elif name is not None:

                cursor.execute(
                    """
                    UPDATE users
                    SET name = %s
                    WHERE id = %s
                    RETURNING id, name, email, role;
                    """,
                    (name, user_id)
                )

            else:

                cursor.execute(
                    """
                    UPDATE users
                    SET role = %s
                    WHERE id = %s
                    RETURNING id, name, email, role;
                    """,
                    (role, user_id)
                )

            updated_user = cursor.fetchone()

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "message": "User updated successfully",
                "user": {
                    "id": updated_user[0],
                    "name": updated_user[1],
                    "email": updated_user[2],
                    "role": updated_user[3]
                }
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500

    @app.route(
    "/api/users/<user_id>/",
    methods=["DELETE"]
    )
    @admin_required
    def delete_user(user_id):

        try:
            user_id = int(user_id)

        except ValueError:

            return jsonify({
                "error": "user_id must be an integer"
            }), 400

        if user_id < 1:

            return jsonify({
                "error": "user_id must be greater than 0"
            }), 400

        user = get_user_by_id(user_id)

        if user is None:

            return jsonify({
                "error": "User not found"
            }), 404

        try:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM users
                WHERE id = %s
                RETURNING id, name, email, role;
                """,
                (user_id,)
            )

            deleted_user = cursor.fetchone()

            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "message": "User deleted successfully",
                "user": {
                    "id": deleted_user[0],
                    "name": deleted_user[1],
                    "email": deleted_user[2],
                    "role": deleted_user[3]
                }
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500     
        
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

            return jsonify(
                deal
            ), 200

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

            if not isinstance(
                data["content"],
                str
            ):

                return jsonify({
                    "error": "content must be a string"
                }), 400

            if not data["content"].strip():

                return jsonify({
                    "error": "content cannot be empty"
                }), 400

        if "product_link" in data:

            if not isinstance(
                data["product_link"],
                str
            ):

                return jsonify({
                    "error": "product_link must be a string"
                }), 400

            if not data["product_link"].strip():

                return jsonify({
                    "error": "product_link cannot be empty"
                }), 400

        if "image_path" in data:

            if not isinstance(
                data["image_path"],
                str
            ):

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

            print(
                "SCRAPER FINISHED"
            )

        except Exception as e:

            print(
                "SCRAPER ERROR:",
                str(e)
            )

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


    @app.route(
        "/api/logs/",
        methods=["GET"]
    )
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


    @app.route(
        "/api/deals/bulk-update/",
        methods=["POST"]
    )
    def bulk_update():

        if not request.is_json:

            return jsonify({
                "error": "Request body must be JSON"
            }), 400

        data = request.get_json()

        if not isinstance(data, dict):

            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        message_ids = data.get(
            "message_ids"
        )

        updates = data.get(
            "updates"
        )

        if not isinstance(
            message_ids,
            list
        ) or not message_ids:

            return jsonify({
                "error": "message_ids must be a non-empty list"
            }), 400

        if not isinstance(
            updates,
            dict
        ) or not updates:

            return jsonify({
                "error": "updates must be a non-empty object"
            }), 400

        try:

            result = bulk_update_deals(
                message_ids,
                updates
            )

            return jsonify({
                "message": "Deals updated successfully",
                "data": result
            }), 200

        except ValueError as e:

            return jsonify({
                "error": str(e)
            }), 400

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    @app.route(
        "/api/deals/bulk-delete/",
        methods=["POST"]
    )
    def bulk_delete():

        if not request.is_json:

            return jsonify({
                "error": "Request body must be JSON"
            }), 400

        data = request.get_json()

        if not isinstance(data, dict):

            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        message_ids = data.get(
            "message_ids"
        )

        if not isinstance(
            message_ids,
            list
        ) or not message_ids:

            return jsonify({
                "error": "message_ids must be a non-empty list"
            }), 400

        try:

            result = bulk_delete_deals(
                message_ids
            )

            for image_path in result.get(
                "image_paths",
                []
            ):

                if image_path and os.path.exists(
                    image_path
                ):

                    os.remove(
                        image_path
                    )

            return jsonify({
                "message": "Deals deleted successfully",
                "data": result
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    @app.route(
        "/api/deals/<message_id>/status/",
        methods=["GET"]
    )
    def get_status(message_id):

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

        channel = request.args.get(
            "channel"
        )

        if not channel:

            return jsonify({
                "error": "Channel is required"
            }), 400

        try:

            status = get_deal_status(
                message_id,
                channel
            )

            if status is None:

                return jsonify({
                    "error": "Deal not found"
                }), 404

            return jsonify({
                "message_id": message_id,
                "status": status
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    @app.route(
        "/api/deals/<message_id>/status/",
        methods=["POST"]
    )
    def update_status(message_id):

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

        if not request.is_json:

            return jsonify({
                "error": "Request body must be JSON"
            }), 400

        data = request.get_json()

        if not isinstance(data, dict):

            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        new_status = data.get(
            "status"
        )

        if not new_status:

            return jsonify({
                "error": "status is required"
            }), 400

        if not isinstance(
            new_status,
            str
        ):

            return jsonify({
                "error": "status must be a string"
            }), 400

        new_status = new_status.strip().lower()

        valid_statuses = {
            "new",
            "processed",
            "published",
            "expired",
            "rejected"
        }

        if new_status not in valid_statuses:

            return jsonify({
                "error": "Invalid status"
            }), 400

        channel = request.args.get(
            "channel"
        )

        if not channel:

            return jsonify({
                "error": "Channel is required"
            }), 400

        try:

            result = update_deal_status(
                message_id,
                new_status,
                channel
            )

            if result is None:

                return jsonify({
                    "error": "Deal not found"
                }), 404

            return jsonify({
                "message": "Deal status updated successfully",
                "message_id": message_id,
                "old_status": result["old_status"],
                "new_status": result["new_status"]
            }), 200

        except ValueError as e:

            return jsonify({
                "error": str(e)
            }), 400

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    @app.route(
        "/api/deals/duplicates/",
        methods=["GET"]
    )
    def duplicate_deals():

        channel = request.args.get(
            "channel"
        )

        try:

            duplicates = get_duplicate_deals(
                channel
            )

            return jsonify({
                "count": len(duplicates),
                "results": duplicates
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    @app.route(
        "/api/deals/statistics/",
        methods=["GET"]
    )
    def deal_statistics():

        channel = request.args.get(
            "channel"
        )

        date = request.args.get(
            "date"
        )

        if date:

            try:

                datetime.strptime(
                    date,
                    "%Y-%m-%d"
                )

            except ValueError:

                return jsonify({
                    "error": "date must be in YYYY-MM-DD format"
                }), 400

        try:

            statistics = get_deal_statistics(
                channel=channel,
                date=date
            )

            return jsonify(
                statistics
            ), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    @app.route(
        "/api/scraping-jobs/",
        methods=["POST"]
    )
    def create_job():

        if not request.is_json:

            return jsonify({
                "error": "Request body must be JSON"
            }), 400

        data = request.get_json()

        if not isinstance(data, dict):

            return jsonify({
                "error": "Request body must be a JSON object"
            }), 400

        channel = data.get(
            "channel"
        )

        if channel is None:

            return jsonify({
                "error": "Channel is required"
            }), 400

        if not isinstance(
            channel,
            str
        ):

            return jsonify({
                "error": "Channel must be a string"
            }), 400

        channel = channel.strip()

        if not channel:

            return jsonify({
                "error": "Channel cannot be empty"
            }), 400

        try:

            job = create_scraping_job(
                channel
            )

            return jsonify({
                "message": "Scraping job created successfully",
                "data": job
            }), 201

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    
    
    @app.route(
        "/api/scraping-jobs/<job_id>/",
        methods=["GET"]
    )
    def get_job(job_id):

        try:

            job_id = int(job_id)

        except ValueError:

            return jsonify({
                "error": "job_id must be an integer"
            }), 400

        if job_id < 1:

            return jsonify({
                "error": "job_id must be greater than 0"
            }), 400

        try:

            job = get_scraping_job(
                job_id
            )

            if job is None:

                return jsonify({
                    "error": "Scraping job not found"
                }), 404

            return jsonify(
                job
            ), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    @app.route(
        "/api/scraping-jobs/",
        methods=["GET"]
    )
    def get_jobs():

        status = request.args.get(
            "status"
        )

        channel = request.args.get(
            "channel"
        )

        try:

            page = int(
                request.args.get(
                    "page",
                    "1"
                )
            )

            limit = int(
                request.args.get(
                    "limit",
                    "20"
                )
            )

        except ValueError:

            return jsonify({
                "error": "page and limit must be numbers"
            }), 400

        if page < 1:

            return jsonify({
                "error": "page must be greater than or equal to 1"
            }), 400

        if limit < 1:

            return jsonify({
                "error": "limit must be greater than 0"
            }), 400

        if limit > 100:

            return jsonify({
                "error": "limit cannot be greater than 100"
            }), 400

        try:

            jobs = get_scraping_jobs(
                status=status,
                channel=channel,
                page=page,
                limit=limit
            )

            total_count = count_scraping_jobs(
                status=status,
                channel=channel
            )

            return jsonify({
                "count": total_count,
                "page": page,
                "limit": limit,
                "status": status,
                "channel": channel,
                "results": jobs
            }), 200

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500

    @app.route(
        "/api/scraping-jobs/<job_id>/",
        methods=["PUT"]
    )
    def update_job(job_id):

        try:
            job_id = int(job_id)

        except ValueError:
            return jsonify({
                "error": "job_id must be an integer"
            }), 400

        if job_id < 1:
            return jsonify({
                "error": "job_id must be greater than 0"
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

        status = data.get("status")

        if not status:
            return jsonify({
                "error": "status is required"
            }), 400

        if not isinstance(status, str):
            return jsonify({
                "error": "status must be a string"
            }), 400

        status = status.strip().lower()

        valid_statuses = {
            "pending",
            "running",
            "completed",
            "failed",
            "stopped"
        }

        if status not in valid_statuses:
            return jsonify({
                "error": "Invalid status"
            }), 400

        messages_scraped = data.get(
            "messages_scraped"
        )

        messages_saved = data.get(
            "messages_saved"
        )

        error = data.get(
            "error"
        )

        if messages_scraped is not None:
            if (
                not isinstance(messages_scraped, int)
                or isinstance(messages_scraped, bool)
                or messages_scraped < 0
            ):
                return jsonify({
                    "error": "messages_scraped must be a non-negative integer"
                }), 400

        if messages_saved is not None:
            if (
                not isinstance(messages_saved, int)
                or isinstance(messages_saved, bool)
                or messages_saved < 0
            ):
                return jsonify({
                    "error": "messages_saved must be a non-negative integer"
                }), 400

        if error is not None and not isinstance(error, str):
            return jsonify({
                "error": "error must be a string"
            }), 400

        try:
            updated_job = update_scraping_job(
                job_id=job_id,
                status=status,
                messages_scraped=messages_scraped,
                messages_saved=messages_saved,
                error=error,
                started_at=(status == "running"),
                completed_at=(
                    status in {
                        "completed",
                        "failed",
                        "stopped"
                    }
                )
            )

            if updated_job is None:
                return jsonify({
                    "error": "Scraping job not found"
                }), 404

            return jsonify({
                "message": "Scraping job updated successfully",
                "data": updated_job
            }), 200

        except Exception as e:
            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500


    @app.route(
        "/api/scraping-jobs/<job_id>/retry/",
        methods=["POST"]
    )
    def retry_job(job_id):

        try:

            job_id = int(job_id)

        except ValueError:

            return jsonify({
                "error": "job_id must be an integer"
            }), 400

        if job_id < 1:

            return jsonify({
                "error": "job_id must be greater than 0"
            }), 400

        try:

            result = create_retry_job(
                job_id
            )

            if result is None:

                return jsonify({
                    "error": "Scraping job not found"
                }), 404

            return jsonify({
                "message": "Retry job created successfully",
                "data": result
            }), 201

        except ValueError as e:

            return jsonify({
                "error": str(e)
            }), 400

        except Exception as e:

            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500