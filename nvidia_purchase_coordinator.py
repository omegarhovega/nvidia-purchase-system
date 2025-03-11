#!/usr/bin/env python3
"""
NVIDIA Purchase Coordinator

This script coordinates all components of the NVIDIA purchase system:
1. Runs the cookie-prep session manager to get fresh cf_clearancecookies
2. Periodically refreshes cookies (every 12-15 minutes)
3. Starts the product-scanner/purchase logic
4. Runs the early-warning indicator to detect API status changes
"""
import os
import random
import signal
import subprocess
import sys
import time
import threading
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("coordinator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("coordinator")

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


def format_timestamp():
    """Return a formatted timestamp for console output"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run_session_manager():
    """
    Run the session manager to get fresh cookies.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Starting session manager...")
    print(f"[{format_timestamp()}] Starting cookie refresh...")
    
    try:
        # Navigate to the cookie-prep directory and run session_manager
        cmd = [
            sys.executable,
            "-c",
            "import sys; sys.path.append('.'); import asyncio; from main import main; asyncio.run(main())"
        ]
        
        # Run the process and capture output
        process = subprocess.run(
            cmd,
            cwd=COOKIE_PREP_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        
        # Check if the process was successful
        if process.returncode == 0:
            if os.path.exists(COOKIE_OUTPUT_PATH):
                # Check if the cookies file was updated in the last minute
                if time.time() - os.path.getmtime(COOKIE_OUTPUT_PATH) < 60:
                    logger.info("Session manager completed successfully with fresh cookies")
                    print(f"[{format_timestamp()}] ✅ Cookie refresh successful!")
                    return True
                else:
                    logger.warning("Cookie file exists but may not have been updated")
                    print(f"[{format_timestamp()}] ⚠️ Cookie file exists but may not have been updated")
            else:
                logger.error(f"Cookie file not found at {COOKIE_OUTPUT_PATH}")
                print(f"[{format_timestamp()}] ❌ Cookie file not found!")
                return False
        else:
            logger.error(f"Session manager failed with code {process.returncode}")
            logger.error(f"Error output: {process.stderr}")
            print(f"[{format_timestamp()}] ❌ Cookie refresh failed!")
            print(f"Error: {process.stderr}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error running session manager: {e}")
        print(f"[{format_timestamp()}] ❌ Error running cookie refresh: {e}")
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
            bufsize=1,  # Line buffered
        )
        
        # Create a thread to read and log output
        def log_scanner_output():
            for line in scanner_process.stdout:
                print(line.rstrip())
                logger.info(f"Scanner: {line.rstrip()}")
        
        output_thread = threading.Thread(target=log_scanner_output)
        output_thread.daemon = True
        output_thread.start()
        
        logger.info(f"Product scanner started with PID {scanner_process.pid}")
        print(f"[{format_timestamp()}] ✅ Product scanner started!")
        return scanner_process
    except Exception as e:
        logger.error(f"Error starting product scanner: {e}")
        print(f"[{format_timestamp()}] ❌ Error starting product scanner: {e}")
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
        
        output_thread = threading.Thread(target=log_early_warning_output)
        output_thread.daemon = True
        output_thread.start()
        
        logger.info(f"Early-warning monitor started with PID {early_warning_process.pid}")
        print(f"[{format_timestamp()}] ✅ Early-warning monitor started!")
        return early_warning_process
    except Exception as e:
        logger.error(f"Error starting early-warning monitor: {e}")
        print(f"[{format_timestamp()}] ❌ Error starting early-warning monitor: {e}")
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
            print(f"[{format_timestamp()}] ✅ Product scanner stopped")
        except subprocess.TimeoutExpired:
            logger.warning("Product scanner did not stop gracefully, forcing termination")
            print(f"[{format_timestamp()}] ⚠️ Forcing scanner termination")
            scanner_process.kill()
        except Exception as e:
            logger.error(f"Error stopping product scanner: {e}")
            print(f"[{format_timestamp()}] ❌ Error stopping scanner: {e}")
        
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
            print(f"[{format_timestamp()}] ✅ Early-warning monitor stopped")
        except subprocess.TimeoutExpired:
            logger.warning("Early-warning monitor did not stop gracefully, forcing termination")
            print(f"[{format_timestamp()}] ⚠️ Forcing early-warning termination")
            early_warning_process.kill()
        except Exception as e:
            logger.error(f"Error stopping early-warning monitor: {e}")
            print(f"[{format_timestamp()}] ❌ Error stopping early-warning monitor: {e}")
        
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


def main():
    """
    Main coordinator function.
    """
    # Set up signal handling for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    print(f"\n[{format_timestamp()}] ===== NVIDIA Purchase Coordinator =====")
    logger.info("Coordinator starting")
    
    # Initial cookie preparation
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
        print(f"[{format_timestamp()}] ⚠️ Product scanner exited unexpectedly. Shutting down...")
        return 1
    except KeyboardInterrupt:
        # This should be caught by the signal handler above
        pass
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
