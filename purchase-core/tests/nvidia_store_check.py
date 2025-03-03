#!/usr/bin/env python3
import requests
import sys


def main():
    """
    Check NVIDIA store availability by making a request to the store page.
    This script replicates the functionality of the Rust version.
    """
    try:
        # Create custom headers - using the same as in the Rust script
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.nvidia.com/",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Brave";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
        }

        # Target URL
        url = "https://store.nvidia.com/de-de/geforce/store"

        # Make the request with a timeout of 30 seconds, allow_redirects=True to follow redirects
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)

        # Print response details
        print(f"[INFO] Status Code: {response.status_code}")
        print(f"[INFO] Final URL: {response.url}")
        print(f"[INFO] Response: {len(response.text)} bytes")

        # Print headers
        print("\n[INFO] Response Headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")

        # Print redirect history if any
        if response.history:
            print("\n[INFO] Redirect History:")
            for i, resp in enumerate(response.history):
                print(f"  Redirect {i + 1}: {resp.status_code} - {resp.url}")
        else:
            print("\n[INFO] No redirects occurred")

        return 0
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
