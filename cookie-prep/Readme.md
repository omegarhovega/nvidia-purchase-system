# Cookie Preparation Tool

## Overview

The Cookie Preparation Tool handles browser automation to overcome Cloudflare challenges. The tool's primary purpose is to obtain and store the `cf_clearance` cookie required for programmatic access to direct purchase links on Proshop's website.

## Purpose

Proshop's website employs Cloudflare protection to prevent automated access. This tool:

1. Launches a browser session to navigate to the NVIDIA website
2. Injects a script to activate the "Buy" button using an old purchase link
3. Clicks the "Buy" button which navigates to Proshop and triggers Cloudflare challenges
4. Automatically solves Cloudflare Challenge Page
5. Captures and stores all cookies, particularly the crucial `cf_clearance` cookie
6. Shares these cookies with other components of the NVIDIA Purchase System to be able to directly follow purchase links when they become active without having to clear Cloudflare challenge

## Components

The tool consists of the following modules:

- `main.py`: Entry point that coordinates the cookie preparation process
- `session_manager.py`: Manages browser sessions and handles the core logic
- `browser.py`: Browser setup, navigation, and interceptor injection
- `captcha.py`: CAPTCHA solving functionality using 2Captcha
- `cookies.py`: Cookie capture, storage, and validation
- `config.py`: Configuration settings for the tool
- `logger.py`: Logging functionality

## Integration with Purchase System

This component works in conjunction with:

1. **Product Scanner**: The scanner uses these cookies to check product availability
2. **Purchase Core**: The captured cookies enable the purchase core to authenticate with NVIDIA
3. **Coordinator**: The nvidia_purchase_coordinator.py now features improved real-time output capturing for all cookie-prep messages, with proper formatting and log level identification

## Usage

### Prerequisites

Before running the cookie preparation tool, ensure you have:
1. **2Captcha API Key**: Insert your 2Captcha API key in the .env file (rename .env.example to .env)
2. **Browser**: Install Brave Browser or adjust the browser_executable_path in browser.py to your local Chrome installation
3. **Dependencies**: Install dependencies by running `pip install -r requirements.txt`

### Running the Tool

To run the cookie preparation tool separately (not through the main coordinator script):

```bash
cd cookie-prep/src
python main.py
```

The tool will:
1. Launch a browser session
2. Navigate to NVIDIA's website
3. Activate and click the buy button
4. Attempt to obtain the `cf_clearance` cookie
5. Save cookies to the shared location

### Running via Coordinator (Recommended)

The recommended way to run the cookie-prep tool is via the coordinator script, which provides:
- Automatic handling of cookie refreshes
- Enhanced logging with clear formatting
- Proper integration with other system components

```bash
# From the project root
python nvidia_purchase_coordinator.py

# In silent mode (no sound alerts)
python nvidia_purchase_coordinator.py --silent
```

### Retry Logic

The tool includes built-in retry logic:
- By default, it will attempt up to 3 times to obtain the `cf_clearance` cookie
- Between retries, it will wait 60-120 seconds
- If unsuccessful after all attempts, it will play an audio alert

### Browser Management

By default, the browser will automatically close after completing the cookie capture process. This behavior can be modified in the code by changing the `auto_close_browser` parameter.

## Expected Output

Upon successful execution, the tool will:
1. Save all captured cookies to `shared/scripts/captured_cookies.json`
2. Log confirmation that the `cf_clearance` cookie was obtained
3. Exit gracefully

## Troubleshooting

If the tool fails to obtain the `cf_clearance` cookie:

1. Check your internet connection (Cloudflare might detect VPN connections or inconsistent browser-like headers)
2. Ensure NVIDIA's website is accessible
3. Verify that the Cloudflare challenge is standard (changes to Cloudflare may require updates)
4. Look for error messages in the application logs

## Dependencies

- Python 3.8+
- nodriver (for browser automation)
- asyncio
- Additional dependencies specified in the project's requirements file

## Notes

- The Cloudflare challenge mechanism may change over time, potentially requiring updates to this tool
- The `cf_clearance` cookie typically has a limited validity period (c. 15 minutes)
- This tool should be run periodically to refresh cookies before making purchase attempts (as implemented in the coordinator script)