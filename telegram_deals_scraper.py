from telethon import TelegramClient
from telethon.errors import FloodWaitError

import asyncio
import re
import os
import json

from datetime import datetime


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


# Create Telegram client session
client = TelegramClient(
    "session",
    api_id,
    api_hash
)


# Save execution logs
def write_log(status, message):

    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "message": message
    }


    if os.path.exists(log_file):

        with open(log_file, "r", encoding="utf-8") as file:

            try:
                logs = json.load(file)

            except json.JSONDecodeError:
                logs = []

    else:
        logs = []


    logs.append(log_entry)


    with open(log_file, "w", encoding="utf-8") as file:

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

                if getattr(button, "url", None):

                    return button.url


    if message.text:

        links = re.findall(
            r'https?://\S+',
            message.text
        )

        if links:

            return links[0]


    return "No Link Found"



# Main scraping function
async def main():

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


    # Scrape channels
    for channel_name in channels:

        try:

            print(
                f"\nScraping Channel: {channel_name}"
            )


            channel = await client.get_entity(
                channel_name
            )


            write_log(
                "SUCCESS",
                f"Connected to {channel_name}"
            )


            async for message in client.iter_messages(
                channel,
                limit=message_limit
            ):


                if message.id in processed_ids:

                    print(
                        f"Skipping duplicate message: {message.id}"
                    )

                    continue


                if not (
                    message.text
                    or message.photo
                ):

                    continue


                content = message.text if message.text else ""


                item_link = extract_link(
                    message
                )


                image_path = ""


                # Download image
                if message.photo:

                    image_name = (
                        f"{channel_name}_{message.id}"
                    )


                    image_path = await message.download_media(
                        file=f"{image_folder}/{image_name}"
                    )


                    write_log(
                        "SUCCESS",
                        f"Image downloaded for Message ID {message.id}"
                    )


                deal = {

                    "message_id": message.id,

                    "date": str(message.date),

                    "content": content,

                    "product_link": item_link,

                    "image_path": image_path,

                    "channel": channel_name
                }


                deals.append(deal)

                processed_ids.add(
                    message.id
                )


                write_log(
                    "SUCCESS",
                    f"Scraped Message ID {message.id}"
                )


                print("-" * 40)
                print("Message ID:", message.id)
                print("Date:", message.date)
                print("Content:", content)
                print("Product Link:", item_link)
                print("Image Path:", image_path)
                print("-" * 40)



        except FloodWaitError as e:

            write_log(
                "WARNING",
                f"Flood wait for {e.seconds} seconds"
            )


            print(
                f"Waiting {e.seconds} seconds due to Telegram limit"
            )


            await asyncio.sleep(
                e.seconds
            )


        except Exception as e:

            write_log(
                "ERROR",
                f"{channel_name}: {str(e)}"
            )


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


    write_log(
        "SUCCESS",
        f"{output_file} updated successfully"
    )



# Run scraper
try:

    with client:

        client.loop.run_until_complete(
            main()
        )


except Exception as e:

    write_log(
        "ERROR",
        str(e)
    )

    print(
        "Error:",
        e
    )