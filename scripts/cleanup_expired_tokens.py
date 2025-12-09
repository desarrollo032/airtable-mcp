#!/usr/bin/env python3
"""
Background task to clean up expired OAuth states and tokens
Run this periodically to maintain database hygiene
"""
import asyncio
import os
import logging
from datetime import datetime
from services.token_storage import TokenStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def cleanup_expired_data():
    """Clean up expired OAuth states and tokens"""
    logger.info("Starting cleanup of expired OAuth data...")

    token_storage = TokenStorage()

    try:
        # Clean up expired OAuth states
        await token_storage.cleanup_expired_states()
        logger.info("✅ Cleaned up expired OAuth states")

        # Note: Tokens in Redis expire automatically with TTL
        # For PostgreSQL, we could add similar cleanup here if needed

        logger.info("✅ Cleanup completed successfully")

    except Exception as e:
        logger.error(f"❌ Cleanup failed: {str(e)}")
        raise

async def main():
    """Main cleanup function"""
    while True:
        try:
            await cleanup_expired_data()
        except Exception as e:
            logger.error(f"Cleanup task failed: {str(e)}")

        # Run cleanup every hour
        logger.info("⏰ Next cleanup in 1 hour...")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    # Run once for manual execution
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--once":
        asyncio.run(cleanup_expired_data())
    else:
        # Run as continuous background task
        asyncio.run(main())
