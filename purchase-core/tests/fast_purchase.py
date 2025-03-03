#!/usr/bin/env python3
import json
import time
import requests
import os


def fast_purchase(purchase_url):
    # Start timing
    start_time = time.time()

    # Load cookies from file - using an absolute path to the file
    cookies_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "shared",
        "scripts",
        "captured_cookies.json",
    )
    try:
        with open(cookies_path, "r") as f:
            cookie_data = json.load(f)
            # The cookies are in a nested "cookies" array
            if "cookies" in cookie_data:
                all_cookies = cookie_data["cookies"]
                print(f"[INFO] Loaded {len(all_cookies)} cookies from {cookies_path}")
            else:
                print("[ERROR] No 'cookies' field found in the JSON file")
                return False
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[ERROR] Failed to load cookies: {e}")
        return False

    # Check for CloudFlare clearance cookie
    cf_clearance = next(
        (cookie["value"] for cookie in all_cookies if cookie["name"] == "cf_clearance"),
        None,
    )
    if not cf_clearance:
        print("[ERROR] No Cloudflare clearance cookie found")
        return False
    else:
        print(f"[INFO] Found cf_clearance cookie: {cf_clearance[:10]}...")

    # Create session with cookies
    session = requests.Session()
    for cookie in all_cookies:
        session.cookies.set(
            name=cookie["name"], value=cookie["value"], domain=cookie.get("domain", "")
        )

    # Set browser fingerprinting headers - MUST match original
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://marketplace.nvidia.com/",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
    }

    print(f"[INFO] Making request to {purchase_url}")

    try:
        # Make request with automatic redirect handling
        response = session.get(
            purchase_url,
            headers=headers,
            timeout=30,  # Reduced timeout for faster response
            allow_redirects=True,  # Let requests handle redirects automatically
        )

        # Print the final URL after all redirects
        print(f"[INFO] Final URL after redirects: {response.url}")

        # Save the final HTML page
        html_output_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "shared",
            "scripts",
            "final_page.html",
        )
        with open(html_output_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"[INFO] Saved final page HTML to {html_output_path}")

        # Record redirect history
        redirect_history = []
        for r in response.history:
            redirect_history.append(
                {
                    "from": r.url,
                    "to": r.headers.get("Location", ""),
                    "status_code": r.status_code,
                }
            )

        # Save redirect history
        redirects_output_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "shared",
            "scripts",
            "redirect_history.json",
        )
        with open(redirects_output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "final_url": response.url,
                    "redirects": redirect_history,
                },
                f,
                indent=2,
            )
        print(f"[INFO] Saved redirect history to {redirects_output_path}")

        # Save updated cookies
        updated_cookies = [
            {"name": c.name, "value": c.value, "domain": c.domain}
            for c in session.cookies
        ]

        # Save in the same format as the original file
        output_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "cookies": updated_cookies,
        }

        # Save cookies to shared/scripts/captured_cookies.json
        cookies_output_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "shared",
            "scripts",
            "captured_purchase_cookies.json",
        )
        with open(cookies_output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"[INFO] Saved cookies to {cookies_output_path}")

        # Check for ASP.NET_SessionId cookie
        asp_session = session.cookies.get("ASP.NET_SessionId")
        if asp_session:
            print(f"[INFO] Found ASP.NET_SessionId cookie: {asp_session}")
        else:
            print("[WARNING] No ASP.NET_SessionId cookie found")

        # Report results
        elapsed_time = time.time() - start_time
        print(
            f"[INFO] Request completed with status {response.status_code} in {elapsed_time:.2f}s"
        )
        return response.status_code < 400

    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        elapsed_time = time.time() - start_time
        print(f"[INFO] Request failed after {elapsed_time:.2f}s")
        return False


if __name__ == "__main__":
    # Default test URL (same as in original code)
    default_url = "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D"

    # Run the purchase function
    if fast_purchase(default_url):
        print("[INFO] Purchase attempt completed successfully!")
    else:
        print("[ERROR] Purchase attempt failed")
