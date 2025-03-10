import time
import asyncio
import random

# Now import with fully qualified package names
from config import (
    NVIDIA_URL,
    NVIDIA_BUY_BUTTON_SELECTOR,
)
from browser import (
    setup_browser,
    inject_interceptor,
    handle_new_tab,
    handle_overlay,
)
from captcha import (
    solve_captcha,
    submit_captcha_solution,
)
from cookies import save_all_cookies, check_for_cf_clearance
from logger import logger


async def run_session_manager(attempt=1, max_attempts=3, auto_close_browser=False):
    """
    Main function to handle Cloudflare challenge and capture cookies.
    Includes retry logic if cf_clearance cookie is not obtained.

    Args:
        attempt: Current attempt number
        max_attempts: Maximum number of attempts before giving up
        auto_close_browser: If True, browser will be closed automatically after completing the task
                            If False, browser will remain open until manually closed by the user
    """
    browser = None

    try:
        logger.info(f"Starting session manager attempt {attempt}/{max_attempts}")

        # 1. Setup browser, navigate to page, inject code to show buy button, handle cookie overlay
        browser = await setup_browser()
        tab = await browser.get(NVIDIA_URL)
        await inject_interceptor(browser, tab)
        await handle_overlay(tab)

        # 2. Click buy button and handle Cloudflare check with 2captcha, obtaining cf_clearance cookie
        try:
            buy_button = await tab.select(NVIDIA_BUY_BUTTON_SELECTOR)
            await buy_button.click()
            logger.info("Buy button clicked successfully")

            await handle_new_tab(browser)
            await asyncio.sleep(3)

            if len(browser.tabs) >= 2:
                # Select the new tab opening after clicking buy button
                new_tab = browser.tabs[1]
                logger.info("Starting Cloudflare challenge solution")

                # Wait for turnstile parameters
                params_wait_start = time.time()
                while not hasattr(new_tab, "turnstile_params"):
                    if time.time() - params_wait_start > 30:
                        logger.warning("Timeout waiting for Turnstile parameters")
                        break
                    await asyncio.sleep(0.5)

                # Solve captcha if parameters are available
                if hasattr(new_tab, "turnstile_params"):
                    params = new_tab.turnstile_params
                    logger.info(f"Using captured parameters: {params}")

                    token = solve_captcha(params)
                    if token:
                        logger.info("Submitting captcha solution...")
                        success = await submit_captcha_solution(new_tab, token)

                        if success:
                            logger.info("Captcha solution submitted successfully")
                            logger.info("Waiting for Cloudflare to process solution...")
                            await asyncio.sleep(2)
                        else:
                            logger.error("Failed to submit captcha solution")
                    else:
                        logger.error("Failed to get captcha token from 2captcha")
                else:
                    logger.error("Failed to capture Turnstile parameters")
            else:
                logger.warning("No new tab detected for Cloudflare challenge")

        except Exception as e:
            logger.error(f"Error during purchase process: {e}")

        # 3. Save cookies and close browser only if auto_close_browser is True
        logger.info("Saving all cookies regardless of challenge completion status...")
        await asyncio.sleep(5)
        await save_all_cookies(browser, tab)

        if auto_close_browser:
            logger.info("Closing browser...")
            if browser:
                try:
                    # Check if browser has the stop method before calling it
                    if hasattr(browser, "stop") and callable(getattr(browser, "stop")):
                        await browser.stop()
                    else:
                        logger.warning(
                            "Browser object does not have a stop method or it's not callable"
                        )
                except Exception as e:
                    logger.error(f"Error closing browser: {e}")
        else:
            logger.info("Browser will remain open until manually closed by the user")

        # 4. Check for cf_clearance cookie in file
        # Wait a bit for file operations to complete
        time.sleep(1)

        if check_for_cf_clearance():
            logger.info("Successfully obtained cf_clearance cookie!")
            return True
        else:
            logger.warning("Failed to obtain cf_clearance cookie")

            if attempt < max_attempts:
                retry_delay = random.randint(60, 120)
                logger.info(
                    f"Retrying in {retry_delay} seconds (attempt {attempt + 1}/{max_attempts})..."
                )
                await asyncio.sleep(retry_delay)
                return await run_session_manager(attempt + 1, max_attempts, auto_close_browser)
            else:
                logger.error(
                    f"Failed to obtain cf_clearance cookie after {max_attempts} attempts"
                )
                try:
                    # Play error sound
                    import winsound

                    winsound.Beep(1000, 1000)  # Beep at 1000 Hz for 1 second
                except Exception as e:
                    logger.error(f"Failed to play error sound: {e}")

                logger.info("Browser will be closed automatically...")
                # logger.info("Keeping the window open for 15 seconds...")
                # await asyncio.sleep(15)
                return False

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        import traceback

        logger.error(traceback.format_exc())

    finally:
        # Close browser only if auto_close_browser is True
        if auto_close_browser and browser:
            try:
                # Check if browser has the stop method before calling it
                if hasattr(browser, "stop") and callable(getattr(browser, "stop")):
                    await browser.stop()
                else:
                    logger.warning(
                        "Browser object does not have a stop method or it's not callable"
                    )
            except Exception as e:
                logger.error(f"Error closing browser: {e}")

    return False