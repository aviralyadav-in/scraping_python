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


# Check if deal already exists in PostgreSQL

def deal_exists(message_id, channel):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT 1
    FROM deals
    WHERE message_id = %s
    AND channel = %s
    LIMIT 1;
    """

    cursor.execute(
        query,
        (
            message_id,
            channel
        )
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result is not None


# Save deal

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
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (channel, message_id)
    DO NOTHING
    RETURNING message_id;
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

    row = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    if row is None:
        return False

    return True


# Save log

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
    VALUES (NOW(), %s, %s);
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


# Get deals with channel/date filters

def get_deals(
    channel=None,
    from_date=None,
    to_date=None,
    page=1,
    limit=100
):
    conn = get_connection()
    cursor = conn.cursor()

    offset = (page - 1) * limit

    conditions = []
    values = []

    if channel:
        conditions.append(
            "channel = %s"
        )

        values.append(
            channel
        )

    if from_date:
        conditions.append(
            "date::date >= %s"
        )

        values.append(
            from_date
        )

    if to_date:
        conditions.append(
            "date::date <= %s"
        )

        values.append(
            to_date
        )

    query = """
    SELECT
        message_id,
        date,
        content,
        product_link,
        image_path,
        channel
    FROM deals
    """

    if conditions:
        query += " WHERE "
        query += " AND ".join(
            conditions
        )

    query += """
    ORDER BY date DESC
    LIMIT %s
    OFFSET %s;
    """

    values.extend(
        [
            limit,
            offset
        ]
    )

    cursor.execute(
        query,
        values
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    deals = []

    for row in rows:
        deals.append(
            {
                "message_id": row[0],
                "date": str(row[1]),
                "content": row[2],
                "product_link": row[3],
                "image_path": row[4],
                "channel": row[5]
            }
        )

    return deals


# Get single deal

def get_deal(
    message_id,
    channel=None
):
    conn = get_connection()
    cursor = conn.cursor()

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
        WHERE message_id = %s
        AND channel = %s;
        """

        cursor.execute(
            query,
            (
                message_id,
                channel
            )
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
        WHERE message_id = %s;
        """

        cursor.execute(
            query,
            (
                message_id,
            )
        )

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


# Count deals with channel/date filters

def count_deals(
    channel=None,
    from_date=None,
    to_date=None
):
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    values = []

    if channel:
        conditions.append(
            "channel = %s"
        )

        values.append(
            channel
        )

    if from_date:
        conditions.append(
            "date::date >= %s"
        )

        values.append(
            from_date
        )

    if to_date:
        conditions.append(
            "date::date <= %s"
        )

        values.append(
            to_date
        )

    query = """
    SELECT COUNT(*)
    FROM deals
    """

    if conditions:
        query += " WHERE "
        query += " AND ".join(
            conditions
        )

    cursor.execute(
        query,
        values
    )

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count


# Update deal

def update_deal(
    message_id,
    content,
    product_link,
    image_path,
    channel=None
):
    conn = get_connection()
    cursor = conn.cursor()

    if channel:
        query = """
        UPDATE deals
        SET
            content = %s,
            product_link = %s,
            image_path = %s
        WHERE message_id = %s
        AND channel = %s
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
                message_id,
                channel
            )
        )

    else:
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

def delete_deal(
    message_id,
    channel=None
):
    conn = get_connection()
    cursor = conn.cursor()

    if channel:
        query = """
        DELETE FROM deals
        WHERE message_id = %s
        AND channel = %s
        RETURNING
            message_id,
            image_path;
        """

        cursor.execute(
            query,
            (
                message_id,
                channel
            )
        )

    else:
        query = """
        DELETE FROM deals
        WHERE message_id = %s
        RETURNING
            message_id,
            image_path;
        """

        cursor.execute(
            query,
            (
                message_id,
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
        "image_path": row[1]
    }


# Get logs

def get_logs(page=1,
    limit=10
):
    conn = get_connection()
    cursor = conn.cursor()
    offset = (page - 1) * limit

    query = """
    SELECT
        time,
        status,
        message
    FROM logs
    ORDER BY time DESC
    LIMIT %s
    OFFSET %s;
    """

    cursor.execute(
        query,
        (
            limit,
            offset
        )
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    logs = []

    for row in rows:
        logs.append(
            {
                "time": str(row[0]),
                "status": row[1],
                "message": row[2]
            }
        )

    return logs