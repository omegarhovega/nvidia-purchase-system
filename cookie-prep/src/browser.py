import nodriver
import json
import asyncio
import time
from dotenv import load_dotenv
from config import (
    NVIDIA_INJECT_SCRIPT,
    PROSHOP_URL,
    PROSHOP_INJECT_SCRIPT,
)
from logger import logger

# Load environment variables from .env file with 2Captcha API key
load_dotenv()

async def setup_browser():
    """
    Setup nodriver Browser with Brave browser and configurations.
    """
    try:
        browser = await nodriver.Browser.create(
            browser_executable_path="C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
            # browser_executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe",
            # "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
            browser_args=[
                "--window-size=1920,1080",
                "--lang=de-DE",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-brave-extension",
            ],
            headless=False,
        )
        await browser.start()
        return browser
    except Exception as e:
        logger.error(f"Failed to setup browser: {e}")
        raise


async def inject_interceptor(browser, tab):
    """
    Inject a JavaScript snippet via CDP to override network methods for requests targeting the NVIDIA API.
    """
    try:
        # Injection into API response for availability check
        mock_response = {
            "success": True,
            "timestamp": int(time.time() * 1000),
            "map": None,
            "listMap": [
                {
                    "is_active": "true",
                    "product_url": PROSHOP_URL,
                    "price": "2329",
                    "fe_sku": "Pro5090FE_DE",
                    "locale": "DE",
                }
            ],
        }
        interceptor_js = NVIDIA_INJECT_SCRIPT % (json.dumps(mock_response))

        # Enable the page domain
        await browser.main_tab.send(nodriver.cdp.page.enable())

        # Inject the script
        script_id = await browser.main_tab.send(
            nodriver.cdp.page.add_script_to_evaluate_on_new_document(
                source=interceptor_js
            )
        )

        logger.info(
            f"Interceptor injected via CDP successfully with script ID: {script_id}"
        )

        # Refresh the page to ensure the script is evaluated
        await tab.send(nodriver.cdp.page.reload(ignore_cache=True))

    except Exception as e:
        logger.error(f"Failed to inject interceptor: {e}")
        raise


async def handle_overlay(tab):
    """
    Handle the cookie consent overlay by clicking the 'Fertig' button.
    """
    try:
        # Wait for the overlay to appear
        overlay_button_selector = (
            "button[aria-label='Fertig']"  # Ensure this selector is correct
        )
        overlay_button = await tab.select(overlay_button_selector)
        if overlay_button:
            await overlay_button.click()
            logger.info("Overlay dismissed successfully")
        else:
            logger.warning("Overlay button not found, skipping dismissal.")
    except Exception as e:
        logger.error(f"Failed to dismiss overlay: {e}")


async def handle_new_tab(browser):
    """
    Handle the new tab opened by Cloudflare and inject the JavaScript to intercept turnstile.render call parameters.
    """
    try:
        if len(browser.tabs) >= 2:
            new_tab = browser.tabs[1]
            logger.info("New tab detected, preparing to inject script.")

            # First set up the console monitoring
            await new_tab.send(nodriver.cdp.runtime.enable())

            # Then enable page and inject the main script
            await new_tab.send(nodriver.cdp.page.enable())

            # Set up console message handler using CDP events
            async def handle_console_api_called(event):
                try:
                    if "Turnstile parameters:" in str(event.args[0].value):
                        params_json = event.args[1].value
                        turnstile_params = json.loads(params_json)
                        logger.info(
                            f"Captured Turnstile parameters: {turnstile_params}"
                        )
                        new_tab.turnstile_params = turnstile_params
                except Exception as e:
                    logger.error(f"Error processing console message: {e}")

            # Add handler for console messages
            new_tab.add_handler(
                nodriver.cdp.runtime.ConsoleAPICalled, handle_console_api_called
            )

            # Remove the console.log override from the end of the script
            turnstile_interceptor_js = PROSHOP_INJECT_SCRIPT

            await new_tab.send(
                nodriver.cdp.runtime.evaluate(
                    expression=turnstile_interceptor_js,
                    await_promise=True,
                )
            )
            logger.info("Turnstile interceptor script executed in new tab.")

            # Optional: Wait for parameters with timeout
            start_time = time.time()
            while not hasattr(new_tab, "turnstile_params"):
                if time.time() - start_time > 10:
                    logger.warning("Timeout waiting for Turnstile parameters")
                    break
                await asyncio.sleep(0.1)

        else:
            logger.warning("No new tab detected.")
    except Exception as e:
        logger.error(f"Failed to handle new tab: {e}")
        raise
