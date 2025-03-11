import time
import asyncio
import random
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


async def run_session_manager(attempt, max_attempts, auto_close_browser):
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

        # Setup the browser and prepare the page
        browser, tab = await setup_browser_environment()
        
        # Click buy button and handle Cloudflare challenge
        await handle_buy_button_click(browser, tab)
        
        # Save cookies and handle browser closure
        await save_cookies_and_cleanup(browser, tab, auto_close_browser)
        
        # Check for successful cookie acquisition
        if await check_cookie_success(attempt, max_attempts, auto_close_browser):
            return True
            
        # We'll only reach here if cookie check failed but we should retry
        return False
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

    finally:
        # Close browser only if auto_close_browser is True and hasn't been closed yet
        if auto_close_browser and browser:
            await close_browser(browser)


async def setup_browser_environment():
    """
    Set up the browser environment, navigate to the NVIDIA page,
    inject necessary interceptors, and handle overlays.
    
    Returns:
        tuple: (browser, tab) - The browser instance and main tab
    """
    browser = await setup_browser()
    tab = await browser.get(NVIDIA_URL)
    await inject_interceptor(browser, tab)
    await handle_overlay(tab)
    
    return browser, tab


async def handle_buy_button_click(browser, tab):
    """
    Click the buy button and handle the resulting Cloudflare challenge if present.
    
    Args:
        browser: The browser instance
        tab: The main browser tab
    """
    try:
        buy_button = await tab.select(NVIDIA_BUY_BUTTON_SELECTOR)
        await buy_button.click()
        logger.info("Buy button clicked successfully")

        await handle_new_tab(browser)
        await asyncio.sleep(3)

        # Check if we have at least 2 tabs (Proshop/Cloudflare challenge opens in new tab)
        if len(browser.tabs) < 2:
            logger.warning("No new tab detected for Cloudflare challenge")
            return
            
        # Process the new tab for Cloudflare challenge
        await process_cloudflare_challenge(browser)

    except Exception as e:
        logger.error(f"Error during buy button process: {e}")


async def save_cookies_and_cleanup(browser, tab, auto_close_browser):
    """
    Save cookies and handle browser cleanup.
    
    Args:
        browser: The browser instance
        tab: The main browser tab
        auto_close_browser: Whether to automatically close the browser
    """
    logger.info("Saving all cookies regardless of challenge completion status...")
    await asyncio.sleep(5)
    await save_all_cookies(browser, tab)

    # Handle browser closure if needed
    if auto_close_browser:
        await close_browser(browser)
    else:
        logger.info("Browser will remain open until manually closed by the user")


async def check_cookie_success(attempt, max_attempts, auto_close_browser):
    """
    Check if the cf_clearance cookie was successfully obtained.
    Handle retry logic if not.
    
    Args:
        attempt: Current attempt number
        max_attempts: Maximum number of attempts
        auto_close_browser: Whether to automatically close the browser
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Wait a bit for file operations to complete
    time.sleep(1)

    # Return true if we got the cookie
    if check_for_cf_clearance():
        logger.info("Successfully obtained cf_clearance cookie!")
        return True
        
    # If we get here, we failed to obtain the cookie
    logger.warning("Failed to obtain cf_clearance cookie")
    
    # Return if max attempts reached
    if attempt >= max_attempts:
        logger.error(f"Failed to obtain cf_clearance cookie after {max_attempts} attempts")
        try:
            # Play error sound
            import winsound
            winsound.Beep(1000, 1000)  # Beep at 1000 Hz for 1 second
        except Exception as e:
            logger.error(f"Failed to play error sound: {e}")

        logger.info("Browser will be closed automatically...")
        return False
        
    # Retry if we have attempts left
    retry_delay = random.randint(60, 120)
    logger.info(f"Retrying in {retry_delay} seconds (attempt {attempt + 1}/{max_attempts})...")
    await asyncio.sleep(retry_delay)
    return await run_session_manager(attempt + 1, max_attempts, auto_close_browser)


async def process_cloudflare_challenge(browser):
    """
    Process the Cloudflare challenge in the new tab.
    """
    new_tab = browser.tabs[1]
    logger.info("Starting Cloudflare challenge solution")

    # Wait for turnstile parameters
    params_wait_start = time.time()
    while not hasattr(new_tab, "turnstile_params"):
        if time.time() - params_wait_start > 30:
            logger.warning("Timeout waiting for Turnstile parameters")
            return  # Guard clause: Return early if timeout
        await asyncio.sleep(0.5)

    # Guard clause: Return if no turnstile parameters
    if not hasattr(new_tab, "turnstile_params"):
        logger.error("Failed to capture Turnstile parameters")
        return
        
    params = new_tab.turnstile_params
    logger.info(f"Using captured parameters: {params}")

    token = solve_captcha(params)
    
    # Guard clause: Return if no token
    if not token:
        logger.error("Failed to get captcha token from 2captcha")
        return
        
    logger.info("Submitting captcha solution...")
    success = await submit_captcha_solution(new_tab, token)

    if not success:
        logger.error("Failed to submit captcha solution")
        return
        
    logger.info("Captcha solution submitted successfully")
    logger.info("Waiting for Cloudflare to process solution...")
    await asyncio.sleep(2)


async def close_browser(browser):
    """Helper function to close the browser."""
    if not browser:
        return
        
    try:
        logger.info("Closing browser...")
        # Check if browser has the stop method before calling it
        if hasattr(browser, "stop") and callable(getattr(browser, "stop")):
            # Store the result and check if it's awaitable
            stop_result = browser.stop()
            if stop_result is not None and hasattr(stop_result, "__await__"):
                await stop_result
            else:
                # If stop_result is not awaitable, log it but don't try to await it
                logger.info("Browser stop function returned non-awaitable result")
        else:
            logger.warning("Browser object does not have a stop method or it's not callable")
    except Exception as e:
        logger.error(f"Error closing browser: {e}")