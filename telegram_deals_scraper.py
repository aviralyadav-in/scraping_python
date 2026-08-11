from database import save_deal, save_log, deal_exists

from telethon import TelegramClient
from telethon.errors import FloodWaitError

import asyncio
import re
import os
import json
import requests
import random
import threading

from datetime import datetime


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/137.0 Safari/537.36"
]


with open(
    "config.json",
    "r",
    encoding="utf-8"
) as file:

    config = json.load(file)


api_id = config["api_id"]
api_hash = config["api_hash"]
channels = config["channels"]
message_limit = config["message_limit"]
image_folder = config["image_folder"]
output_file = config["output_file"]
log_file = config["log_file"]


def write_log(status, message):

    log_entry = {
        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "status": status,
        "message": message
    }

    if os.path.exists(log_file):

        try:

            with open(
                log_file,
                "r",
                encoding="utf-8"
            ) as file:

                logs = json.load(file)

        except (
            json.JSONDecodeError,
            FileNotFoundError
        ):

            logs = []

    else:

        logs = []

    logs.append(log_entry)

    try:

        save_log(
            status,
            message
        )

    except Exception as e:

        print(
            "DATABASE LOG ERROR:",
            str(e)
        )

    try:

        with open(
            log_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                logs,
                file,
                indent=4,
                ensure_ascii=False
            )

    except Exception as e:

        print(
            "JSON LOG ERROR:",
            str(e)
        )


def extract_link(message):

    if message.buttons:

        for row in message.buttons:

            for button in row:

                if getattr(
                    button,
                    "url",
                    None
                ):

                    return button.url

    if message.text:

        links = re.findall(
            r'https?://\S+',
            message.text
        )

        if links:

            return links[0]

    return "No Link Found"


def validate_product_link(url):

    if not url or url == "No Link Found":

        return

    try:

        headers = {
            "User-Agent": random.choice(
                USER_AGENTS
            )
        }

        print(
            "Using User-Agent:",
            headers["User-Agent"]
        )

        response = requests.get(
            url,
            headers=headers,
            timeout=5,
            allow_redirects=True
        )

        print(
            "Status Code:",
            response.status_code
        )

        write_log(
            "SUCCESS",
            f"Validated Product Link: {url} | "
            f"Status Code: {response.status_code}"
        )

    except Exception as e:

        print(
            "LINK VALIDATION ERROR:",
            str(e)
        )

        write_log(
            "WARNING",
            f"Link Validation Failed: {str(e)}"
        )


async def main(
    client,
    channel_name,
    limit,
    stop_event
):

    os.makedirs(
        image_folder,
        exist_ok=True
    )

    messages_scraped = 0
    messages_saved = 0
    current_deal = None
    count = 0

    print()
    print("=" * 60)
    print(
        f"SCRAPING CHANNEL: {channel_name}"
    )
    print(
        f"SCRAPING LIMIT: {limit}"
    )
    print("=" * 60)

    try:

        channel = await client.get_entity(
            channel_name
        )

        print(
            "Connected Successfully"
        )

        print(
            "Channel ID:",
            channel.id
        )

        print(
            "Channel Title:",
            getattr(
                channel,
                "title",
                "Unknown"
            )
        )

        write_log(
            "SUCCESS",
            f"Connected to {channel_name}"
        )

        print(
            "Fetching messages..."
        )

        async for message in client.iter_messages(
            channel,
            limit=int(limit)
        ):

            if stop_event.is_set():

                print(
                    "STOP REQUEST DETECTED"
                )

                break

            count += 1

            print()
            print(
                f"Reading Message {count}"
            )

            print(
                "Message ID:",
                message.id
            )

            print(
                "Has photo:",
                bool(message.photo)
            )

            if deal_exists(
                message.id,
                channel_name
            ):

                print(
                    f"Skipping Duplicate in PostgreSQL: {message.id}"
                )

                continue

            if not (
                message.text
                or message.photo
            ):

                print(
                    "Skipping empty message"
                )

                continue

            if stop_event.is_set():

                print(
                    "STOP REQUEST DETECTED"
                )

                break

            item_link = extract_link(
                message
            )

            print(
                "Product Link:",
                item_link
            )

            validate_product_link(
                item_link
            )

            if stop_event.is_set():

                print(
                    "STOP REQUEST DETECTED"
                )

                break

            content = (
                message.text
                if message.text
                else ""
            )

            image_path = ""

            if message.photo:

                image_name = (
                    f"{channel_name}_{message.id}.jpg"
                )

                image_file = os.path.join(
                    image_folder,
                    image_name
                )

                print(
                    "Downloading image..."
                )

                try:

                    downloaded_path = (
                        await message.download_media(
                            file=image_file
                        )
                    )

                    if (
                        downloaded_path
                        and os.path.exists(
                            downloaded_path
                        )
                    ):

                        image_path = downloaded_path

                        print(
                            "Image downloaded successfully:",
                            downloaded_path
                        )

                        write_log(
                            "SUCCESS",
                            f"Image downloaded for "
                            f"Message ID {message.id}: "
                            f"{downloaded_path}"
                        )

                    else:

                        print(
                            "Image download failed"
                        )

                        write_log(
                            "ERROR",
                            f"Image download failed for "
                            f"Message ID {message.id}"
                        )

                except Exception as e:

                    image_path = ""

                    print(
                        "IMAGE DOWNLOAD ERROR:",
                        str(e)
                    )

                    write_log(
                        "ERROR",
                        f"Image download failed for "
                        f"Message ID {message.id}: "
                        f"{str(e)}"
                    )

            deal = {
                "message_id": message.id,
                "date": str(message.date),
                "content": content,
                "product_link": item_link,
                "image_path": image_path,
                "channel": channel_name
            }

            current_deal = (
                f"Message ID {message.id}"
            )

            print(
                "Saving deal to PostgreSQL..."
            )

            try:

                saved = save_deal(
                    deal
                )

                if saved is False:

                    print(
                        f"Deal already exists in PostgreSQL: {message.id}"
                    )

                    write_log(
                        "INFO",
                        f"Deal already exists for "
                        f"Message ID {message.id}"
                    )

                    continue

                print(
                    "Deal saved to PostgreSQL"
                )

            except Exception as e:

                print(
                    "DATABASE SAVE ERROR:",
                    str(e)
                )

                write_log(
                    "ERROR",
                    f"Database save failed for "
                    f"Message ID {message.id}: "
                    f"{str(e)}"
                )

                continue

            messages_scraped += 1
            messages_saved += 1

            write_log(
                "SUCCESS",
                f"Scraped Message ID {message.id}"
            )

            print(
                "-" * 50
            )

            print(
                "Message ID:",
                message.id
            )

            print(
                "Date:",
                message.date
            )

            print(
                "Content:",
                content
            )

            print(
                "Product Link:",
                item_link
            )

            print(
                "Image Path:",
                image_path
            )

            print(
                "Messages Scraped:",
                messages_scraped
            )

            print(
                "Messages Saved:",
                messages_saved
            )

            print(
                "-" * 50
            )

        print()
        print(
            "Messages Read:",
            count
        )

    except FloodWaitError as e:

        print(
            f"Flood wait for {e.seconds} seconds"
        )

        write_log(
            "WARNING",
            f"Flood wait for {e.seconds} seconds"
        )

        await asyncio.sleep(
            e.seconds
        )

    except Exception as e:

        print(
            "CHANNEL ERROR:",
            str(e)
        )

        write_log(
            "ERROR",
            f"{channel_name}: {str(e)}"
        )

        raise

    try:

        from database import get_deals

        all_deals = get_deals(
            channel=channel_name,
            page=1,
            limit=10000
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                all_deals,
                file,
                indent=4,
                ensure_ascii=False
            )

        print()
        print(
            f"Data exported from PostgreSQL to {output_file}"
        )

    except Exception as e:

        print(
            "JSON EXPORT ERROR:",
            str(e)
        )

        write_log(
            "ERROR",
            f"Could not export PostgreSQL data to JSON: {str(e)}"
        )

    if stop_event.is_set():

        write_log(
            "STOPPED",
            f"Scraping stopped for {channel_name}. "
            f"Messages scraped: {messages_scraped}, "
            f"Messages saved: {messages_saved}"
        )

    else:

        write_log(
            "SUCCESS",
            f"Scraping completed for {channel_name}. "
            f"Messages scraped: {messages_scraped}, "
            f"Messages saved: {messages_saved}"
        )

    print()
    print("=" * 60)
    print("SCRAPING RESULT")
    print(
        "Messages Scraped:",
        messages_scraped
    )
    print(
        "Messages Saved:",
        messages_saved
    )
    print(
        "Current Deal:",
        current_deal
    )
    print("=" * 60)

    return {
        "messages_scraped": messages_scraped,
        "messages_saved": messages_saved,
        "current_deal": current_deal
    }


def start_scraper(
    channel_name,
    limit,
    stop_event
):

    channel_name = channel_name.strip().lower()

    print()
    print("=" * 60)
    print("INSIDE START_SCRAPER")
    print(
        "Channel:",
        channel_name
    )
    print(
        "Limit:",
        limit
    )
    print("=" * 60)

    client = TelegramClient(
        "session",
        api_id,
        api_hash
    )

    try:

        with client:

            result = client.loop.run_until_complete(
                main(
                    client,
                    channel_name,
                    int(limit),
                    stop_event
                )
            )

            print(
                "START_SCRAPER RESULT:",
                result
            )

            return result

    except Exception as e:

        print(
            "SCRAPER ERROR:",
            str(e)
        )

        write_log(
            "ERROR",
            str(e)
        )

        raise


if __name__ == "__main__":

    stop_event = threading.Event()

    start_scraper(
        channels[0],
        message_limit,
        stop_event
    )