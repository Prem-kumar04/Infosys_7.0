import asyncio

from app.db.session import test_db_connection


async def main():
    try:
        await test_db_connection()
        print("Database connection successful!")
    except Exception as error:
        print("Database connection failed!")
        print(error)


if __name__ == "__main__":
    asyncio.run(main())