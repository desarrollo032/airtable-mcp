#!/usr/bin/env python3
"""
Wait for database dependencies to be ready
"""
import os
import time
import redis
import asyncpg
import sys

def wait_for_redis():
    """Wait for Redis to be ready"""
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))

    print(f"⏳ Waiting for Redis at {redis_host}:{redis_port}...")
    for i in range(30):
        try:
            r = redis.Redis(host=redis_host, port=redis_port)
            r.ping()
            print("✅ Redis is ready!")
            return True
        except redis.ConnectionError:
            print(f"   Attempt {i+1}/30 failed, retrying...")
            time.sleep(2)
    return False

async def wait_for_postgres():
    """Wait for PostgreSQL to be ready"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return True

    print("⏳ Waiting for PostgreSQL...")
    for i in range(30):
        try:
            conn = await asyncpg.connect(database_url)
            await conn.close()
            print("✅ PostgreSQL is ready!")
            return True
        except Exception as e:
            print(f"   Attempt {i+1}/30 failed: {e}, retrying...")
            time.sleep(2)
    return False

async def main():
    """Main wait function"""
    redis_ready = wait_for_redis()
    postgres_ready = await wait_for_postgres()

    if redis_ready and postgres_ready:
        print("🎉 All dependencies are ready!")
        sys.exit(0)
    else:
        print("❌ Some dependencies failed to start")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
