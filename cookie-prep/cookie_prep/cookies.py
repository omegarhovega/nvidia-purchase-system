import os
import nodriver
import json
import datetime
import traceback
from logger import logger


async def save_all_cookies(browser, tab):
    """
    Save all cookies from all tabs in the browser.
    """
    try:
        # JSON with name/value/domain
        try:
            simple_cookies = []
            all_tabs = browser.tabs if browser and hasattr(browser, "tabs") else []
            # Dictionary to track unique cookies by name+domain combination
            unique_cookies = {}

            for tab in all_tabs:
                if tab is None:
                    logger.warning("Skipping None tab when saving cookies")
                    continue

                try:
                    response = await tab.send(nodriver.cdp.storage.get_cookies())
                    if hasattr(response, "__iter__"):
                        for cookie in response:
                            try:
                                name = (
                                    getattr(cookie, "name", None)
                                    if not isinstance(cookie, dict)
                                    else cookie.get("name")
                                )
                                value = (
                                    getattr(cookie, "value", None)
                                    if not isinstance(cookie, dict)
                                    else cookie.get("value")
                                )
                                domain = (
                                    getattr(cookie, "domain", None)
                                    if not isinstance(cookie, dict)
                                    else cookie.get("domain")
                                )
                                if name and value:
                                    cookie_data = {
                                        "name": str(name),
                                        "value": str(value),
                                    }
                                    if domain:
                                        cookie_data["domain"] = str(domain)

                                    # Use name+domain as unique identifier
                                    cookie_key = f"{name}_{domain or ''}"
                                    unique_cookies[cookie_key] = cookie_data
                            except Exception:
                                pass

                except Exception as e:
                    logger.error(f"Failed to get cookies from tab: {e}")

            # Convert dictionary values to list after removing duplicates
            simple_cookies = list(unique_cookies.values())

            # Add timestamp to the JSON data structure
            timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
            cookies_data = {"timestamp": timestamp, "cookies": simple_cookies}

            # Ensure file is written with proper encoding and no BOM
            # Use an absolute path to ensure the file is saved in the correct location
            cookies_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "shared",
                "scripts",
                "captured_cookies.json",
            )
            with open(cookies_file_path, "w", encoding="utf-8") as f:
                json.dump(cookies_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Cookie data saved to json at {cookies_file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
            logger.error(traceback.format_exc())
            return False

    except Exception as e:
        logger.error(f"Failed to save cookies: {e}")
        logger.error(traceback.format_exc())
        return False
