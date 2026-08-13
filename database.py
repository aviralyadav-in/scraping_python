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
        channel,
        status
    )
    VALUES (%s, %s, %s, %s, %s, %s, 'new')
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
        channel,
        status
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
                "channel": row[5],
                "status": row[6]
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
            channel,
            status
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
            channel,
            status
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
        "channel": row[5],
        "status": row[6]
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
            channel,
            status;
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
            channel,
            status;
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
        "channel": row[5],
        "status": row[6]
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

def get_logs(
    page=1,
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

# ADVANCED API FUNCTIONS

# API 1 - Bulk update deals

def bulk_update_deals(message_ids, updates):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        valid_fields = {
            "status",
            "content",
            "product_link",
            "image_path"
        }

        invalid_fields = set(updates.keys()) - valid_fields

        if invalid_fields:
            raise ValueError(
                f"Invalid field(s): {', '.join(invalid_fields)}"
            )

        if not updates:
            raise ValueError(
                "Updates cannot be empty"
            )

        unique_ids = list(
            dict.fromkeys(message_ids)
        )

        placeholders = ", ".join(
            ["%s"] * len(unique_ids)
        )

        cursor.execute(
            f"""
            SELECT message_id
            FROM deals
            WHERE message_id IN ({placeholders});
            """,
            unique_ids
        )

        existing_ids = {
            row[0]
            for row in cursor.fetchall()
        }

        failed_ids = [
            message_id
            for message_id in unique_ids
            if message_id not in existing_ids
        ]

        set_parts = []
        values = []

        for field, value in updates.items():

            if field == "status":

                valid_statuses = {
                    "new",
                    "processed",
                    "published",
                    "expired",
                    "rejected"
                }

                if value not in valid_statuses:
                    raise ValueError(
                        "Invalid status"
                    )

            set_parts.append(
                f"{field} = %s"
            )

            values.append(value)

        values.extend(unique_ids)

        cursor.execute(
            f"""
            UPDATE deals
            SET {", ".join(set_parts)}
            WHERE message_id IN ({placeholders});
            """,
            values
        )

        updated = cursor.rowcount

        conn.commit()

        return {
            "updated": updated,
            "failed": len(failed_ids),
            "failed_ids": failed_ids
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


# API 2 - Bulk delete deals

def bulk_delete_deals(message_ids):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        unique_ids = list(
            dict.fromkeys(message_ids)
        )

        placeholders = ", ".join(
            ["%s"] * len(unique_ids)
        )

        cursor.execute(
            f"""
            SELECT message_id, image_path
            FROM deals
            WHERE message_id IN ({placeholders});
            """,
            unique_ids
        )

        rows = cursor.fetchall()

        existing_ids = {
            row[0]
            for row in rows
        }

        failed_ids = [
            message_id
            for message_id in unique_ids
            if message_id not in existing_ids
        ]

        image_paths = [
            row[1]
            for row in rows
            if row[1]
        ]

        cursor.execute(
            f"""
            DELETE FROM deals
            WHERE message_id IN ({placeholders});
            """,
            unique_ids
        )

        deleted = cursor.rowcount

        conn.commit()

        return {
            "deleted": deleted,
            "failed": len(failed_ids),
            "failed_ids": failed_ids,
            "image_paths": image_paths
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


# API 3 - Get deal status

def get_deal_status(message_id, channel=None):
    conn = get_connection()
    cursor = conn.cursor()

    if channel:

        cursor.execute(
            """
            SELECT status
            FROM deals
            WHERE message_id = %s
            AND channel = %s;
            """,
            (
                message_id,
                channel
            )
        )

    else:

        cursor.execute(
            """
            SELECT status
            FROM deals
            WHERE message_id = %s;
            """,
            (
                message_id
            )
        )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return row[0]


# API 3 - Update deal status

def update_deal_status(
    message_id,
    new_status,
    channel=None
):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        if channel:

            cursor.execute(
                """
                SELECT status
                FROM deals
                WHERE message_id = %s
                AND channel = %s
                FOR UPDATE;
                """,
                (
                    message_id,
                    channel
                )
            )

        else:

            cursor.execute(
                """
                SELECT status
                FROM deals
                WHERE message_id = %s
                FOR UPDATE;
                """,
                (
                    message_id
                )
            )

        row = cursor.fetchone()

        if row is None:
            conn.rollback()
            return None

        old_status = row[0]

        allowed_transitions = {
            "new": {
                "processed",
                "rejected"
            },
            "processed": {
                "published",
                "rejected"
            },
            "published": {
                "expired"
            },
            "expired": set(),
            "rejected": set()
        }

        if new_status not in {
            "new",
            "processed",
            "published",
            "expired",
            "rejected"
        }:
            raise ValueError(
                "Invalid status"
            )

        if new_status not in allowed_transitions.get(
            old_status,
            set()
        ):
            raise ValueError(
                "Invalid status transition"
            )

        if channel:

            cursor.execute(
                """
                UPDATE deals
                SET status = %s
                WHERE message_id = %s
                AND channel = %s;
                """,
                (
                    new_status,
                    message_id,
                    channel
                )
            )

        else:

            cursor.execute(
                """
                UPDATE deals
                SET status = %s
                WHERE message_id = %s;
                """,
                (
                    new_status,
                    message_id
                )
            )

        conn.commit()

        return {
            "old_status": old_status,
            "new_status": new_status
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


# API 4 - Duplicate deals
def get_duplicate_deals(channel=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        if channel:

            cursor.execute(
                """
                SELECT
                    product_link,
                    COUNT(*) AS count,
                    ARRAY_AGG(message_id ORDER BY message_id) AS message_ids
                FROM deals
                WHERE channel = %s
                AND product_link IS NOT NULL
                AND product_link <> ''
                AND product_link <> 'No Link Found'
                GROUP BY product_link
                HAVING COUNT(*) > 1
                ORDER BY count DESC;
                """,
                (channel,)
            )

        else:

            cursor.execute(
                """
                SELECT
                    product_link,
                    COUNT(*) AS count,
                    ARRAY_AGG(message_id ORDER BY message_id) AS message_ids
                FROM deals
                WHERE product_link IS NOT NULL
                AND product_link <> ''
                AND product_link <> 'No Link Found'
                GROUP BY product_link
                HAVING COUNT(*) > 1
                ORDER BY count DESC;
                """
            )

        rows = cursor.fetchall()

        duplicates = []

        for row in rows:

            duplicates.append(
                {
                    "product_link": row[0],
                    "count": row[1],
                    "message_ids": row[2]
                }
            )

        return duplicates

    finally:
        cursor.close()
        conn.close()

# API 5 - Deal statistics

def get_deal_statistics(
    channel=None,
    date=None
):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        conditions = []
        values = []

        if channel:
            conditions.append(
                "channel = %s"
            )
            values.append(channel)

        if date:
            conditions.append(
                "date::date = %s"
            )
            values.append(date)

        where_clause = ""

        if conditions:
            where_clause = (
                " WHERE "
                + " AND ".join(conditions)
            )

        cursor.execute(
            f"""
            SELECT
                COUNT(*) AS total_deals,
                COUNT(*) FILTER (
                    WHERE image_path IS NOT NULL
                    AND image_path <> ''
                ) AS with_images,
                COUNT(*) FILTER (
                    WHERE image_path IS NULL
                    OR image_path = ''
                ) AS without_images
            FROM deals
            {where_clause};
            """,
            values
        )

        row = cursor.fetchone()

        cursor.execute(
            f"""
            SELECT
                channel,
                COUNT(*)
            FROM deals
            {where_clause}
            GROUP BY channel
            ORDER BY COUNT(*) DESC;
            """,
            values
        )

        channel_rows = cursor.fetchall()

        channels = {}

        for channel_row in channel_rows:
            channels[channel_row[0]] = channel_row[1]

        if date:
            today_deals = row[0]
        else:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM deals
                WHERE date::date = CURRENT_DATE;
                """
            )

            today_deals = cursor.fetchone()[0]

            if channel:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM deals
                    WHERE channel = %s
                    AND date::date = CURRENT_DATE;
                    """,
                    (
                        channel,
                    )
                )

                today_deals = cursor.fetchone()[0]

        return {
            "total_deals": row[0],
            "today_deals": today_deals,
            "with_images": row[1],
            "without_images": row[2],
            "channels": channels
        }

    finally:
        cursor.close()
        conn.close()


# ============================================================
# SCRAPING JOB FUNCTIONS
# ============================================================


# Create scraping job

def create_scraping_job(channel):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO scraping_jobs
            (
                channel,
                status
            )
            VALUES (%s, 'pending')
            RETURNING
                id,
                channel,
                status,
                created_at;
            """,
            (
                channel,
            )
        )

        row = cursor.fetchone()

        conn.commit()

        return {
            "job_id": row[0],
            "channel": row[1],
            "status": row[2],
            "created_at": str(row[3])
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


# Get scraping job

def get_scraping_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            channel,
            status,
            started_at,
            completed_at,
            messages_scraped,
            messages_saved,
            error,
            created_at
        FROM scraping_jobs
        WHERE id = %s;
        """,
        (
            job_id,
        )
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        return None

    return {
        "job_id": row[0],
        "channel": row[1],
        "status": row[2],
        "started_at": str(row[3]) if row[3] else None,
        "completed_at": str(row[4]) if row[4] else None,
        "messages_scraped": row[5],
        "messages_saved": row[6],
        "error": row[7],
        "created_at": str(row[8]) if row[8] else None
    }


# Update scraping job
def update_scraping_job(
    job_id,
    status,
    messages_scraped=None,
    messages_saved=None,
    error=None,
    started_at=False,
    completed_at=False
):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        set_parts = [
            "status = %s"
        ]

        values = [
            status
        ]

        if messages_scraped is not None:

            set_parts.append(
                "messages_scraped = %s"
            )

            values.append(
                messages_scraped
            )

        if messages_saved is not None:

            set_parts.append(
                "messages_saved = %s"
            )

            values.append(
                messages_saved
            )

        if error is not None:

            set_parts.append(
                "error = %s"
            )

            values.append(
                error
            )

        if started_at:

            set_parts.append(
                "started_at = CURRENT_TIMESTAMP"
            )

        if completed_at:

            set_parts.append(
                "completed_at = CURRENT_TIMESTAMP"
            )

        values.append(job_id)

        cursor.execute(
            f"""
            UPDATE scraping_jobs
            SET {", ".join(set_parts)}
            WHERE id = %s
            RETURNING
                id,
                channel,
                status,
                started_at,
                completed_at,
                messages_scraped,
                messages_saved,
                error,
                created_at;
            """,
            values
        )

        row = cursor.fetchone()

        if row is None:
            conn.rollback()
            return None

        conn.commit()

        return {
            "job_id": row[0],
            "channel": row[1],
            "status": row[2],
            "started_at": str(row[3]) if row[3] else None,
            "completed_at": str(row[4]) if row[4] else None,
            "messages_scraped": row[5],
            "messages_saved": row[6],
            "error": row[7],
            "created_at": str(row[8]) if row[8] else None
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()
# Get scraping jobs with filters

def get_scraping_jobs(
    status=None,
    channel=None,
    page=1,
    limit=20
):
    conn = get_connection()
    cursor = conn.cursor()

    offset = (page - 1) * limit

    conditions = []
    values = []

    if status:

        conditions.append(
            "status = %s"
        )

        values.append(
            status
        )

    if channel:

        conditions.append(
            "channel = %s"
        )

        values.append(
            channel
        )

    where_clause = ""

    if conditions:

        where_clause = (
            " WHERE "
            + " AND ".join(conditions)
        )

    query = f"""
    SELECT
        id,
        channel,
        status,
        started_at,
        completed_at,
        messages_scraped,
        messages_saved,
        error,
        created_at
    FROM scraping_jobs
    {where_clause}
    ORDER BY created_at DESC
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

    jobs = []

    for row in rows:

        jobs.append(
            {
                "job_id": row[0],
                "channel": row[1],
                "status": row[2],
                "started_at": str(row[3])
                if row[3] else None,
                "completed_at": str(row[4])
                if row[4] else None,
                "messages_scraped": row[5],
                "messages_saved": row[6],
                "error": row[7],
                "created_at": str(row[8])
                if row[8] else None
            }
        )

    return jobs


# Count scraping jobs

def count_scraping_jobs(
    status=None,
    channel=None
):
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    values = []

    if status:

        conditions.append(
            "status = %s"
        )

        values.append(
            status
        )

    if channel:

        conditions.append(
            "channel = %s"
        )

        values.append(
            channel
        )

    query = """
    SELECT COUNT(*)
    FROM scraping_jobs
    """

    if conditions:

        query += (
            " WHERE "
            + " AND ".join(conditions)
        )

    cursor.execute(
        query,
        values
    )

    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count


# Create retry job

def create_retry_job(previous_job_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                channel,
                status
            FROM scraping_jobs
            WHERE id = %s
            FOR UPDATE;
            """,
            (
                previous_job_id,
            )
        )

        row = cursor.fetchone()

        if row is None:
            conn.rollback()
            return None

        channel = row[0]
        status = row[1]

        if status != "failed":
            conn.rollback()
            raise ValueError(
                "Only failed jobs can be retried"
            )

        cursor.execute(
            """
            INSERT INTO scraping_jobs
            (
                channel,
                status
            )
            VALUES (%s, 'pending')
            RETURNING id;
            """,
            (
                channel,
            )
        )

        new_job_id = cursor.fetchone()[0]

        conn.commit()

        return {
            "job_id": new_job_id,
            "previous_job_id": previous_job_id,
            "channel": channel,
            "status": "pending"
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

# ============================================================
# AUTHENTICATION / USER FUNCTIONS
# ============================================================

# Create user

def create_user(
    name,
    email,
    password_hash,
    role="user"
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash,
                role
            )
            VALUES (%s, %s, %s, %s)
            RETURNING
                id,
                name,
                email,
                role,
                created_at;
            """,
            (
                name,
                email,
                password_hash,
                role
            )
        )

        row = cursor.fetchone()

        conn.commit()

        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3],
            "created_at": str(row[4])
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


# Get user by email

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                password_hash,
                role,
                created_at
            FROM users
            WHERE email = %s;
            """,
            (email,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "password_hash": row[3],
            "role": row[4],
            "created_at": str(row[5])
                if row[5]
                else None
        }

    finally:
        cursor.close()
        conn.close()


# Get user by ID

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                role,
                created_at
            FROM users
            WHERE id = %s;
            """,
            (user_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3],
            "created_at": str(row[4])
                if row[4]
                else None
        }

    finally:
        cursor.close()
        conn.close()


# Get all users

def get_users():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                role,
                created_at
            FROM users
            ORDER BY created_at DESC;
            """
        )

        rows = cursor.fetchall()

        users = []

        for row in rows:
            users.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "role": row[3],
                    "created_at": str(row[4])
                        if row[4]
                        else None
                }
            )

        return users

    finally:
        cursor.close()
        conn.close()
def get_all_users():
    return get_users()