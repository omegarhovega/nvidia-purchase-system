import os
import json
from logger import logger


def check_for_cf_clearance():
    """
    Simple function to check if cf_clearance cookie exists in the captured_cookies.json file.

    Returns:
        bool: True if the cookie exists, False otherwise
    """
    try:
        # Main directory, not the cloudflare subdirectory
        cookies_file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "captured_cookies.json"
        )

        logger.info(f"Checking for cf_clearance in {cookies_file_path}")

        # Check if file exists
        if not os.path.exists(cookies_file_path):
            logger.warning(f"Cookie file does not exist: {cookies_file_path}")
            return False

        # Read the file
        try:
            with open(cookies_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Look for cf_clearance cookie
            if "cookies" not in data:
                logger.warning("No cookies field in JSON data")
                return False

            # Simply check if any cookie has name "cf_clearance"
            found_cf_cookie = False
            for cookie in data.get("cookies", []):
                if isinstance(cookie, dict) and cookie.get("name") == "cf_clearance":
                    found_cf_cookie = True
                    logger.info(
                        f"cf_clearance cookie found with value: {cookie.get('value', 'UNKNOWN')}!"
                    )
                    break

            if found_cf_cookie:
                return True
            else:
                logger.warning("cf_clearance cookie not found")
                return False
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}. The cookies file may be corrupted.")
            return False

    except Exception as e:
        logger.error(f"Error checking for cf_clearance: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return False
