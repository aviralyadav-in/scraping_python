import json
from database import save_deal


with open("deals.json", "r", encoding="utf-8") as file:
    deals = json.load(file)


print("Total deals in JSON:", len(deals))

saved = 0

for deal in deals:
    try:
        save_deal(deal)
        saved += 1
        print("Processed message:", deal["message_id"])

    except Exception as e:
        print(
            "Error saving message",
            deal.get("message_id"),
            ":",
            e
        )


print("--------------------------------")
print("JSON records:", len(deals))
print("Processed:", saved)
print("--------------------------------")