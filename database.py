import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
def get_connection():

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    return conn

def save_deal(deal):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO deals
    (
        message_id,
        date,
        content,
        product_link,
        image_path,
        channel
    )
    VALUES (%s,%s,%s,%s,%s,%s)
    ON CONFLICT (message_id)
    DO NOTHING;
    """

    cursor.execute(
        query,
        (
            deal["message_id"],
            deal["date"],
            deal["content"],
            deal["product_link"],
            deal["image_path"],
            deal["channel"]
        )
    )

    conn.commit()

    cursor.close()
    conn.close()



def save_log(status, message):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO logs
    (
        time,
        status,
        message
    )
    VALUES (NOW(),%s,%s);
    """

    cursor.execute(
        query,
        (
            status,
            message
        )
    )

    conn.commit()

    cursor.close()
    conn.close()


def get_deals(channel=None, page=1, limit=3):
    conn = get_connection()
    cursor = conn.cursor()

    offset = (page - 1) * limit

    if channel:
        query = """
        SELECT
            message_id,
            date,
            content,
            product_link,
            image_path,
            channel
        FROM deals
        WHERE channel = %s
        ORDER BY date DESC
        LIMIT %s OFFSET %s;
        """

        cursor.execute(
            query,
            (channel, limit, offset)
        )

    else:
        query = """
        SELECT
            message_id,
            date,
            content,
            product_link,
            image_path,
            channel
        FROM deals
        ORDER BY date DESC
        LIMIT %s OFFSET %s;
        """

        cursor.execute(
            query,
            (limit, offset)
        )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    deals = []

    for row in rows:
        deals.append({
            "message_id": row[0],
            "date": str(row[1]),
            "content": row[2],
            "product_link": row[3],
            "image_path": row[4],
            "channel": row[5]
        })

    return deals

def get_deal(message_id):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        message_id,
        date,
        content,
        product_link,
        image_path,
        channel
    FROM deals
    WHERE message_id = %s;
    """

    cursor.execute(query, (message_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
        "message_id": row[0],
        "date": str(row[1]),
        "content": row[2],
        "product_link": row[3],
        "image_path": row[4],
        "channel": row[5]
    }
# Count deals
def count_deals(channel=None):

    conn = get_connection()
    cursor = conn.cursor()

    if channel:

        query = """
        SELECT COUNT(*)
        FROM deals
        WHERE channel = %s;
        """

        cursor.execute(
            query,
            (channel,)
        )

    else:

        query = """
        SELECT COUNT(*)
        FROM deals;
        """

        cursor.execute(query)

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count


# Update deal
def update_deal(
    message_id,
    content,
    product_link,
    image_path
):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    UPDATE deals
    SET
        content = %s,
        product_link = %s,
        image_path = %s
    WHERE message_id = %s
    RETURNING
        message_id,
        date,
        content,
        product_link,
        image_path,
        channel;
    """

    cursor.execute(
        query,
        (
            content,
            product_link,
            image_path,
            message_id
        )
    )

    row = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
        "message_id": row[0],
        "date": str(row[1]),
        "content": row[2],
        "product_link": row[3],
        "image_path": row[4],
        "channel": row[5]
    }


# Delete deal
def delete_deal(message_id):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    DELETE FROM deals
    WHERE message_id = %s
    RETURNING
        message_id,
        image_path;
    """

    cursor.execute(
        query,
        (message_id,)
    )

    row = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
        "message_id": row[0],
        "image_path": row[1]
    }
