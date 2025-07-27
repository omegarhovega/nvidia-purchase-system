#!/usr/bin/env python3
"""
NVIDIA Purchase Coordinator

This script coordinates all components of the NVIDIA purchase system:
1. Runs the cookie-prep session manager to get fresh cf_clearance cookies
2. Periodically refreshes cookies (every 12-15 minutes)
3. Starts the product-scanner/purchase logic
4. Runs the early-warning indicator to detect API status changes
"""
import argparse
import os
import random
import signal
import subprocess
import sys
import time
import threading
import winsound
from datetime import datetime
import logging
import codecs

# Configure logging with UTF-8 encoding
def setup_logging():
    # Ensure the logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    # Configure the root logger
    logger = logging.getLogger("coordinator")
    logger.setLevel(logging.INFO)
    
    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(codecs.getwriter('utf-8')(sys.stdout.buffer))
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler('coordinator.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger

# Create logger instance
logger = setup_logging()

# Paths to main components
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_PREP_DIR = os.path.join(BASE_DIR, "cookie-prep", "src")
PRODUCT_SCANNER_DIR = os.path.join(BASE_DIR, "product-scanner")
EARLY_WARNING_DIR = os.path.join(BASE_DIR, "early-warning")
COOKIE_OUTPUT_PATH = os.path.join(BASE_DIR, "shared", "scripts", "captured_cookies.json")

# Global variables
scanner_process = None
early_warning_process = None
shutdown_event = threading.Event()
silent_mode = False  # Default to sound alerts enabled

# Sound settings for different events
SOUND_PATTERNS = {
    "product_available": [(800, 300), (1000, 300), (1200, 500)],  # Three ascending tones
    "early_warning": [(750, 1500)],  # Single tone
    "api_error": [(600, 400), (400, 800)],  # Two descending tones
    "cookie_error": [(600, 400), (400, 800)],  # Two descending tones
    "notification": [(440, 500)]  # Single tone
}


def play_sound(sound_type):
    """
    Play sound alert for the specified event type
    
    Args:
        sound_type (str): Type of event ("product_available", "early_warning", "api_error", "cookie_error", "notification")
    """
    global silent_mode
    
    if silent_mode:
        logger.debug(f"Silent mode: Sound alert for {sound_type} suppressed")
        return
    
    if sound_type in SOUND_PATTERNS:
        try:
            # Play the sequence of tones defined for this sound type
            for freq, duration in SOUND_PATTERNS[sound_type]:
                winsound.Beep(freq, duration)
            logger.debug(f"Sound alert played for {sound_type}")
        except Exception as e:
            logger.error(f"Failed to play sound alert: {e}")
    else:
        logger.error(f"Unknown sound type: {sound_type}")


def format_timestamp():
    """Return a formatted timestamp for console output"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def check_session_cookies():
    """
    Check if session cookies exist and are valid
    Returns True if valid cookies are found, False otherwise
    """
    try:
        if not os.path.exists(COOKIE_OUTPUT_PATH):
            logger.warning("Cookie file not found")
            print(f"[{format_timestamp()}] Cookie file not found")
            return False
            
        # Check if the cookie file has content and contains the cf_clearance cookie
        with open(COOKIE_OUTPUT_PATH, 'r') as file:
            cookie_content = file.read()
            if not cookie_content:
                logger.warning("Cookie file is empty")
                print(f"[{format_timestamp()}] Cookie file is empty")
                return False
                
            if 'cf_clearance' not in cookie_content:
                logger.warning("cf_clearance cookie not found in cookie file")
                print(f"[{format_timestamp()}] cf_clearance cookie not found in cookie file")
                return False
                
        # If we made it here, the cookie file exists and contains cf_clearance
        logger.info("Found valid cookies")
        print(f"[{format_timestamp()}] Found valid cookies")
        return True
    except Exception as e:
        logger.error(f"Error checking session cookies: {str(e)}")
        print(f"[{format_timestamp()}] Error checking session cookies: {str(e)}")
        return False


def run_session_manager():
    """
    Run the session manager to get fresh cookies.
    
    Returns:
        bool: True if successful, False otherwise
    """
    cookie_prep_path = os.path.join(COOKIE_PREP_DIR, "main.py")
    
    if not os.path.exists(cookie_prep_path):
        logger.error(f"Cookie prep script not found at {cookie_prep_path}")
        print(f"[{format_timestamp()}] Cookie prep script not found")
        return False
    
    try:
        logger.info("Running cookie-prep session manager")
        
        # Start the cookie-prep subprocess with no output to console
        process = subprocess.Popen(
            [sys.executable, cookie_prep_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=COOKIE_PREP_DIR,
            text=True,
            encoding='utf-8',  # Specify UTF-8 encoding
            errors='replace'   # Replace invalid characters
        )
        
        # Create threads to read stdout and stderr in real-time
        def read_output(pipe, prefix, is_error=False):
            for line in pipe:
                try:
                    line = line.rstrip()
                    if not line:
                        continue
                        
                    # Let through ALL retry messages, error messages with cookies, and others that might be important
                    if (is_error and "cookie" in line.lower()) or "retry" in line.lower() or "trying again" in line.lower():
                        print(f"[{format_timestamp()}] {line}")
                    elif "failed to obtain" in line.lower() or "obtain cookie failed" in line.lower():
                        print(f"[{format_timestamp()}] {line}")
                    elif "attempt" in line.lower() and "cookie" in line.lower():
                        print(f"[{format_timestamp()}] {line}")
                    elif "session" in line.lower() and "restart" in line.lower():
                        print(f"[{format_timestamp()}] {line}")
                except Exception as e:
                    logger.error(f"Error processing cookie-prep output: {str(e)}")
                    if is_error:
                        print(f"[{format_timestamp()}] Error processing output: {str(e)}")
        
        # Start threads to read output
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "Cookie-Prep"))
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "Cookie-Prep Error", True))
        
        # Make threads daemon so they don't block program exit
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        
        # Start the threads
        stdout_thread.start()
        stderr_thread.start()
        
        # Wait for the process to complete
        process.wait()
        
        # Wait for the output threads to finish
        stdout_thread.join()
        stderr_thread.join()
        
        # Check result based on return code and cookie file
        return_code = process.returncode
        
        if return_code == 0:
            if os.path.exists(COOKIE_OUTPUT_PATH):
                # Check if the cookies file was updated in the last minute
                if time.time() - os.path.getmtime(COOKIE_OUTPUT_PATH) < 60:
                    logger.info("Cookie refresh successful")
                    print(f"[{format_timestamp()}] Cookie refresh successful")
                    return True
                else:
                    logger.warning("Cookie file exists but was not updated")
                    print(f"[{format_timestamp()}] Cookie refresh failed - file not updated")
                    play_sound("cookie_error")
                    return False
            else:
                logger.error(f"Cookie file not found at {COOKIE_OUTPUT_PATH}")
                print(f"[{format_timestamp()}] Cookie refresh failed - file not found")
                play_sound("cookie_error")
                return False
        else:
            logger.error(f"Session manager failed with code {return_code}")
            print(f"[{format_timestamp()}] Cookie refresh failed")
            play_sound("cookie_error")
            return False
    
    except Exception as e:
        logger.error(f"Error running session manager: {str(e)}")
        print(f"[{format_timestamp()}] Cookie refresh failed")
        play_sound("cookie_error")
        return False


def start_product_scanner():
    """
    Start the product scanner process.
    
    Returns:
        subprocess.Popen: The scanner process object
    """
    global scanner_process
    
    logger.info("Starting product scanner...")
    print(f"[{format_timestamp()}] Starting product scanner...")
    
    try:
        # Navigate to product-scanner directory and run cargo run with specific binary
        # The binary name must match exactly what's in Cargo.toml: "product-scanner" (with hyphen)
        scanner_process = subprocess.Popen(
            ["cargo", "run", "--bin", "product-scanner"],  # Explicitly specify the binary name
            cwd=PRODUCT_SCANNER_DIR,
            # Don't capture output so it's displayed in real-time
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',  # Specify UTF-8 encoding
            errors='replace',   # Replace invalid characters
            bufsize=1,  # Line buffered
        )
        
        # Create a thread to read and log output
        def log_scanner_output():
            for line in scanner_process.stdout:
                line = line.rstrip()
                print(line)
                
                # Add specific prefixes for purchase-related logs to make them more identifiable
                if "[INFO] Loading cookies" in line or "[INFO] Loaded" in line or "[INFO] Found cf_clearance" in line:
                    logger.info(f"Purchase: {line}")
                elif "[INFO] Making request" in line or "[INFO] Final URL" in line or "[INFO] Saved" in line:
                    logger.info(f"Purchase: {line}")
                elif "🚀 LAUNCHING PURCHASE" in line or "🔗 Product Link" in line:
                    logger.info(f"Purchase: {line}")
                elif "⏳ Starting purchase attempt" in line or "✅ Purchase process completed" in line:
                    logger.info(f"Purchase: {line}")
                elif "⚠️ Purchase attempt" in line or "❌ All" in line and "purchase attempts failed" in line:
                    logger.info(f"Purchase: {line}")
                else:
                    logger.info(f"Scanner: {line}")
                
                # Check for specific messages to trigger sound alerts
                lower_line = line.lower()
                if "is available" in lower_line or "launching purchase" in lower_line:
                    play_sound("product_available")
                elif "purchase process completed successfully" in lower_line:
                    play_sound("product_available")  # Use same sound for successful purchase
                elif "all purchase attempts failed" in lower_line:
                    play_sound("api_error")  # Use error sound for failed purchase
                elif "api response" in lower_line and "200" not in lower_line:
                    play_sound("api_error")
        
        output_thread = threading.Thread(target=log_scanner_output)
        output_thread.daemon = True
        output_thread.start()
        
        logger.info(f"Product scanner started with PID {scanner_process.pid}")
        print(f"[{format_timestamp()}] Product scanner started!")
        return scanner_process
    except Exception as e:
        logger.error(f"Error starting product scanner: {e}")
        print(f"[{format_timestamp()}] Error starting product scanner: {e}")
        return None


def start_early_warning():
    """
    Start the early-warning monitor process.
    
    Returns:
        subprocess.Popen: The early-warning process object
    """
    global early_warning_process
    
    logger.info("Starting early-warning monitor...")
    print(f"[{format_timestamp()}] Starting early-warning monitor...")
    
    try:
        # Navigate to early-warning directory and run cargo run with verbose flag
        early_warning_process = subprocess.Popen(
            ["cargo", "run", "--release", "--", "--verbose", "--interval", "30"],
            cwd=EARLY_WARNING_DIR,
            # Don't capture output so it's displayed in real-time
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',  # Specify UTF-8 encoding
            errors='replace',   # Replace invalid characters
            bufsize=1,  # Line buffered
            env={**os.environ, "RUST_LOG": "info"}  # Set logging level for the early-warning component
        )
        
        # Create a thread to read and log output
        def log_early_warning_output():
            for line in early_warning_process.stdout:
                line = line.rstrip()
                # Only print if line is not empty
                if line:
                    print(f"[Early Warning] {line}")
                    logger.info(f"Early Warning: {line}")
                    
                    # Check for specific messages to trigger sound alerts
                    lower_line = line.lower()
                    if "detected changes" in lower_line or "status change" in lower_line:
                        play_sound("early_warning")
                    elif "error" in lower_line:
                        play_sound("api_error")
        
        output_thread = threading.Thread(target=log_early_warning_output)
        output_thread.daemon = True
        output_thread.start()
        
        logger.info(f"Early-warning monitor started with PID {early_warning_process.pid}")
        print(f"[{format_timestamp()}] Early-warning monitor started!")
        return early_warning_process
    except Exception as e:
        logger.error(f"Error starting early-warning monitor: {e}")
        print(f"[{format_timestamp()}] Error starting early-warning monitor: {e}")
        return None


def stop_product_scanner():
    """Stop the product scanner process if it's running."""
    global scanner_process
    
    if scanner_process:
        logger.info("Stopping product scanner...")
        print(f"[{format_timestamp()}] Stopping product scanner...")
        
        try:
            # Send Ctrl+C to the process
            if sys.platform == 'win32':
                # Windows-specific way to terminate process
                scanner_process.terminate()
            else:
                # Unix-like systems
                scanner_process.send_signal(signal.SIGINT)
                
            # Wait for the process to terminate
            scanner_process.wait(timeout=10)
            logger.info("Product scanner stopped")
            print(f"[{format_timestamp()}] Product scanner stopped")
        except subprocess.TimeoutExpired:
            logger.warning("Product scanner did not stop gracefully, forcing termination")
            print(f"[{format_timestamp()}] Forcing scanner termination")
            scanner_process.kill()
        except Exception as e:
            logger.error(f"Error stopping product scanner: {e}")
            print(f"[{format_timestamp()}] Error stopping scanner: {e}")
        
        scanner_process = None


def stop_early_warning():
    """Stop the early-warning monitor process if it's running."""
    global early_warning_process
    
    if early_warning_process:
        logger.info("Stopping early-warning monitor...")
        print(f"[{format_timestamp()}] Stopping early-warning monitor...")
        
        try:
            # Send Ctrl+C to the process
            if sys.platform == 'win32':
                # Windows-specific way to terminate process
                early_warning_process.terminate()
            else:
                # Unix-like systems
                early_warning_process.send_signal(signal.SIGINT)
                
            # Wait for the process to terminate
            early_warning_process.wait(timeout=10)
            logger.info("Early-warning monitor stopped")
            print(f"[{format_timestamp()}] Early-warning monitor stopped")
        except subprocess.TimeoutExpired:
            logger.warning("Early-warning monitor did not stop gracefully, forcing termination")
            print(f"[{format_timestamp()}] Forcing early-warning termination")
            early_warning_process.kill()
        except Exception as e:
            logger.error(f"Error stopping early-warning monitor: {e}")
            print(f"[{format_timestamp()}] Error stopping early-warning monitor: {e}")
        
        early_warning_process = None


def cookie_refresh_scheduler():
    """
    Thread function that periodically runs the session manager to refresh cookies.
    """
    while not shutdown_event.is_set():
        # Wait 12-15 minutes before refreshing cookies
        minutes = random.randint(12, 15)
        seconds = minutes * 60
        
        logger.info(f"Scheduled next cookie refresh in {minutes} minutes")
        print(f"[{format_timestamp()}] Scheduled next cookie refresh in {minutes} minutes")
        
        # Sleep in small increments to check for shutdown
        for _ in range(seconds):
            if shutdown_event.is_set():
                return
            time.sleep(1)
        
        # Run session manager to refresh cookies
        run_session_manager()


def signal_handler(sig, frame):
    """
    Signal handler for graceful shutdown on Ctrl+C and other signals.
    """
    print(f"\n[{format_timestamp()}] Shutdown signal received, cleaning up...")
    logger.info("Shutdown signal received")
    
    # Set the shutdown event to stop background threads
    shutdown_event.set()
    
    # Stop the scanner and early-warning monitor
    stop_product_scanner()
    stop_early_warning()
    
    print(f"[{format_timestamp()}] Coordinator shutdown complete")
    sys.exit(0)


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(description="NVIDIA Purchase Coordinator")
    parser.add_argument("--silent", action="store_true", help="Run in silent mode (no sound alerts)")
    return parser.parse_args()


def main():
    """
    Main coordinator function.
    """
    global silent_mode
    
    # Parse command-line arguments
    args = parse_arguments()
    silent_mode = args.silent
    
    if silent_mode:
        logger.info("Running in silent mode (sound alerts disabled)")
        print(f"[{format_timestamp()}] Running in silent mode (sound alerts disabled)")
    else:
        logger.info("Sound alerts enabled")
        print(f"[{format_timestamp()}] Sound alerts enabled")
    
    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    print(f"\n[{format_timestamp()}] ===== NVIDIA Purchase Coordinator =====")
    logger.info("Coordinator starting")
    
    # Initial notification sound
    play_sound("notification")
    
    # Initial cookie preparation
    if not check_session_cookies():
        if not run_session_manager():
            print(f"[{format_timestamp()}] Failed to get initial cookies, exiting")
            return 1
    
    # Start cookie refresh in a background thread
    refresh_thread = threading.Thread(target=cookie_refresh_scheduler)
    refresh_thread.daemon = True
    refresh_thread.start()
    
    # Start the product scanner
    scanner = start_product_scanner()
    if not scanner:
        print(f"[{format_timestamp()}] Failed to start product scanner, exiting")
        return 1
    
    # Start the early-warning monitor
    early_warning = start_early_warning()
    if not early_warning:
        print(f"[{format_timestamp()}] Failed to start early-warning monitor")
        logger.warning("Early-warning monitor failed to start, continuing without it")
        # Continue execution, don't exit
    
    print(f"[{format_timestamp()}] Coordinator running. Press Ctrl+C to exit.")
    
    # Wait for the scanner to complete (it should run indefinitely)
    try:
        scanner.wait()
        logger.warning("Product scanner exited unexpectedly")
        print(f"[{format_timestamp()}] Product scanner exited unexpectedly. Shutting down...")
        play_sound("api_error")
        return 1
    except KeyboardInterrupt:
        # This should be caught by the signal handler above
        pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
