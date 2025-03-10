import asyncio
from logger import logger
from session_manager import run_session_manager
from cookies import check_for_cf_clearance

async def main():
    """
    Main entry point that calls run_session_manager with retry logic.
    Set auto_close_browser to True to automatically close the browser after completion.
    """
    try:
        result = await run_session_manager(attempt=1, max_attempts=3, auto_close_browser=True)

        # Double-check the result with check_for_cf_clearance function
        cf_cookie_exists = check_for_cf_clearance()
        
        if result and cf_cookie_exists:
            logger.info("Session manager completed successfully")
            # Browser is automatically closed
            # logger.info("Browser will remain open until manually closed by the user")
            # Wait indefinitely to keep the process running while the browser is open
            # while True:
            #     await asyncio.sleep(60)
        elif result and not cf_cookie_exists:
            logger.warning(
                "Session manager reported success but cf_clearance cookie was not found"
            )
            # Browser is automatically closed
            # logger.info("Browser will remain open until manually closed by the user")
            # Wait indefinitely to keep the process running while the browser is open
            # while True:
            #    await asyncio.sleep(60)
        else:
            logger.warning("Session manager failed to obtain cf_clearance cookie")
            # Browser is automatically closed
            # logger.info("Browser will remain open until manually closed by the user")
            # Wait indefinitely to keep the process running while the browser is open
            # while True:
            #     await asyncio.sleep(60)
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
