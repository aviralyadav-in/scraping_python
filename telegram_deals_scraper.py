from database import save_deal, save_log
from telethon import TelegramClient
from telethon.errors import FloodWaitError
import asyncio
import re
import os
import json
import requests
import random

from datetime import datetime


# HTTP headers used while validating product links

USER_AGENTS = [

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0 Safari/537.36",

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",

    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/18.0 Safari/605.1.15",

    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/137.0 Safari/537.36"

]


# Load project configuration

with open("config.json", "r", encoding="utf-8") as file:

    config = json.load(file)


api_id = config["api_id"]
api_hash = config["api_hash"]
channels = config["channels"]
message_limit = config["message_limit"]
image_folder = config["image_folder"]
output_file = config["output_file"]
log_file = config["log_file"]


# Save execution logs

def write_log(status, message):

    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "message": message
    }


    if os.path.exists(log_file):

        with open(
            log_file,
            "r",
            encoding="utf-8"
        ) as file:

            try:

                logs = json.load(file)

            except json.JSONDecodeError:

                logs = []

    else:

        logs = []


    logs.append(log_entry)

    save_log(
        status,
        message
    )


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


# Extract product link

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


# Validate the extracted product link using a User-Agent

def validate_product_link(url):

    if not url or url == "No Link Found":

        return


    try:

        # Display the User-Agent being used

        headers = {
            "User-Agent": random.choice(USER_AGENTS)
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

        write_log(
            "WARNING",
            f"Link Validation Failed: {str(e)}"
        )


# Main scraping function

async def main(client, channel_name, message_limit):

    os.makedirs(
        image_folder,
        exist_ok=True
    )


    # Load previous scraped data

    if os.path.exists(output_file):

        with open(
            output_file,
            "r",
            encoding="utf-8"
        ) as file:

            try:

                deals = json.load(file)

            except json.JSONDecodeError:

                deals = []

    else:

        deals = []


    # Store existing message IDs

    processed_ids = {
        deal["message_id"]
        for deal in deals
    }


    try:

        print(
            f"\nScraping Channel: {channel_name}"
        )


        channel = await client.get_entity(
            channel_name
        )


        print(
            "Connected Successfully"
        )


        print(
            "Channel ID :",
            channel.id
        )


        print(
            "Channel Title :",
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


        count = 0
        messages_scraped = 0
        messages_saved = 0


        async for message in client.iter_messages(
            channel,
            limit=message_limit
        ):

            count += 1


            print(
                f"Reading Message {count}"
            )
            print("Has photo:", bool(message.photo))
            print("Media type:", type(message.media))


            # Skip duplicate messages

            if message.id in processed_ids:

                print(
                    f"Skipping Duplicate : {message.id}"
                )

                continue


            # Extract and validate product link

            item_link = extract_link(
                message
            )

            validate_product_link(
                item_link
            )


            # Skip empty messages

            if not (
                message.text
                or message.photo
            ):

                continue

            messages_scraped += 1

            content = (
                message.text
                if message.text
                else ""
            )


            image_path = ""


            # UPDATED IMAGE DOWNLOAD SECTION ONLY

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


                print(
                    "Image path:",
                    image_file
                )


                try:

                    downloaded_path = await message.download_media(
                        file=image_file
                    )


                    print(
                        "Downloaded path returned:",
                        downloaded_path
                    )


                    if (
                        downloaded_path
                        and os.path.exists(
                            downloaded_path
                        )
                    ):

                        file_size = os.path.getsize(
                            downloaded_path
                        )


                        print(
                            "Image downloaded successfully"
                        )


                        print(
                            "File size:",
                            file_size,
                            "bytes"
                        )


                        image_path = downloaded_path


                        write_log(
                            "SUCCESS",
                            f"Image downloaded for "
                            f"Message ID {message.id}: "
                            f"{downloaded_path}"
                        )


                    else:

                        image_path = ""


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



            # END OF UPDATED IMAGE DOWNLOAD SECTION

            deal = {

                "message_id": message.id,

                "date": str(
                    message.date
                ),

                "content": content,

                "product_link": item_link,

                "image_path": image_path,

                "channel": channel_name

            }


            deals.append(
                deal
            )


            save_deal(
                deal
            )
            messages_saved += 1

            processed_ids.add(
                message.id
            )


            write_log(
                "SUCCESS",
                f"Scraped Message ID {message.id}"
            )


            print(
                "-" * 40
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
                "-" * 40
            )


        print(
            "Messages Read :",
            count
        )


    except FloodWaitError as e:

        write_log(
            "WARNING",
            f"Flood wait for {e.seconds} seconds"
        )


        print(
            f"Waiting {e.seconds} seconds..."
        )


        await asyncio.sleep(
            e.seconds
        )


    except Exception as e:

        print(
            "CHANNEL ERROR :",
            e
        )


        write_log(
            "ERROR",
            f"{channel_name}: {str(e)}"
        )
        raise


    # Save scraped data

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            deals,
            file,
            indent=4,
            ensure_ascii=False
        )


    print(
        f"\nData saved successfully in {output_file}"
    )


    print(
        "Total Deals Saved :",
        len(deals)
    )


    write_log(
        "SUCCESS",
        f"{output_file} updated successfully"
    )

    return {
    "messages_scraped": messages_scraped,
    "messages_saved": messages_saved
    } 


def start_scraper(channel_name, limit):

    print(
        "=" * 50
    )


    print(
        "Inside start_scraper"
    )


    print(
        "Channel :",
        channel_name
    )


    print(
        "Limit :",
        limit
    )


    print(
        "=" * 50
    )


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
                    int(limit)
                )
            )
            return result

    except Exception as e:

        print(
            "SCRAPER ERROR :",
            e
        )


        write_log(
            "ERROR",
            str(e)
        )
        
        raise
    
if __name__ == "__main__":

    start_scraper(
        channels[0],
        message_limit
    )