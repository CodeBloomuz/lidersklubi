import aiosqlite
from config import DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS applicants (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id     INTEGER UNIQUE,
                username        TEXT,
                full_name       TEXT,
                fakultet        TEXT,
                yonalish        TEXT,
                guruh           TEXT,
                phone           TEXT,
                interest        TEXT,
                interview_reply TEXT DEFAULT NULL,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                date     TEXT,
                time     TEXT,
                location TEXT,
                sent_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def add_applicant(telegram_id, username, full_name,
                        fakultet, yonalish, guruh, phone, interest):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO applicants
            (telegram_id, username, full_name, fakultet, yonalish, guruh, phone, interest)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (telegram_id, username, full_name, fakultet, yonalish, guruh, phone, interest))
        await db.commit()


async def get_applicant(telegram_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM applicants WHERE telegram_id = ?", (telegram_id,)
        ) as cur:
            return await cur.fetchone()


async def get_all_applicants():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM applicants ORDER BY created_at DESC"
        ) as cur:
            return await cur.fetchall()


async def set_interview_reply(telegram_id, reply: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE applicants SET interview_reply = ? WHERE telegram_id = ?",
            (reply, telegram_id)
        )
        await db.commit()


async def save_interview(date, time, location):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO interviews (date, time, location) VALUES (?, ?, ?)",
            (date, time, location)
        )
        await db.commit()


async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM applicants") as cur:
            total = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM applicants WHERE interview_reply = 'yes'"
        ) as cur:
            coming = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM applicants WHERE interview_reply = 'no'"
        ) as cur:
            not_coming = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT COUNT(*) FROM applicants WHERE interview_reply IS NULL"
        ) as cur:
            no_reply = (await cur.fetchone())[0]
        return {
            "total": total,
            "coming": coming,
            "not_coming": not_coming,
            "no_reply": no_reply
        }
