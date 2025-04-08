# NVIDIA Product Scanner

A high-performance Rust application that monitors NVIDIA's API for GPU availability and automatically initiates the purchase process when products become available.

## Features

- Continuous monitoring of NVIDIA's FE inventory API
- Automatic purchase initiation when products are detected
- Robust error handling with exponential backoff retries
- Configurable request parameters via TOML config
- Detailed logging with timestamps
- Test mode for verifying purchase workflow
- Cookie-based authentication handling
- CloudFlare protection bypass support

## Components

1. **Product Checker** (`product_checker.rs`)
   - Monitors NVIDIA API endpoints
   - Handles request retries and backoff
   - Parses API responses
   - Detects product availability

2. **Purchase Executor** (`execute_purchase.rs`)
   - Manages purchase request execution
   - Handles cookie-based authentication
   - Processes CloudFlare protection
   - Tracks redirect chains
   - Saves session data and debug info

3. **Main Controller** (`main.rs`)
   - Loads configuration from TOML
   - Manages monitoring lifecycle
   - Handles graceful shutdown
   - Provides test mode functionality

## Usage

```bash
# Normal operation
cargo run --release

# Test mode (simulates product availability)
cargo run --release -- --test

# Test mode with error simulation
cargo run --release -- --test-error
```

## Configuration

The application uses `config/default.toml` for settings:
- API endpoints and timeouts
- Request headers and user agent
- Retry parameters
- Sleep intervals between checks

## Logging

- Console output with timestamps
- Detailed debug logs in verbose mode
- Purchase attempt results
- API response tracking
- Error reporting with stack traces
