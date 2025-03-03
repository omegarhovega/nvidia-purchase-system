import nodriver
import os
from logger import logger
from twocaptcha import TwoCaptcha
from dotenv import load_dotenv

# Load environment variables from .env file for 2Captcha API key
load_dotenv()


def solve_captcha(params):
    """
    Solves the Turnstile captcha using the 2Captcha service.

    Args:
        params (dict): The intercepted Turnstile parameters.

    Returns:
        str: The solved captcha token or None if failed.
    """
    try:
        apikey = os.getenv("APIKEY_2CAPTCHA")
        if not apikey:
            logger.error("2Captcha API key not found in environment variables")
            return None

        solver = TwoCaptcha(apikey)

        result = solver.turnstile(
            sitekey=params["websiteKey"],
            url=params["websiteURL"],
            action=params.get("action", ""),
            data=params.get("data", ""),
            pagedata=params.get("pagedata", ""),
            useragent=params.get("userAgent", ""),
        )

        logger.info("Captcha solved successfully")
        return result["code"]
    except Exception as e:
        logger.error(f"Failed to solve captcha: {e}")
        return None


async def submit_captcha_solution(tab, token):
    """
    Submits the solved captcha token to the page.

    Args:
        tab: The browser tab object.
        token (str): The solved captcha token.
    """
    try:
        if not token:
            logger.error("No token provided to submit")
            return False

        # Execute the callback with the token
        script = f"window.tsCallback('{token}')"
        await tab.send(
            nodriver.cdp.runtime.evaluate(expression=script, await_promise=True)
        )

        logger.info("Captcha token submitted successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to submit captcha solution: {e}")
        return False
