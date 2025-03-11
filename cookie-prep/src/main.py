import asyncio
from logger import logger
from session_manager import run_session_manager

async def main():
    """
    Main entry point that calls run_session_manager with retry logic.
    Args:
        attempt (int): Initial attempt number
        max_attempts (int): Maximum number of attempts before giving up and waiting for next scheduled run
        auto_close_browser (bool): If True, browser will be closed automatically after completing the task
    """
    try:
        await run_session_manager(attempt=1, max_attempts=3, auto_close_browser=True)
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user. Exiting...")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process terminated by user")
