# NVIDIA Product Scanner

## Overview

The Product Scanner is a high-performance Rust component that continuously monitors NVIDIA's API for GPU availability. When a product becomes available, it can automatically initiate the purchase process.

## Recent Improvements

### Code Refactoring
- Improved code organization with proper separation of concerns
  - Moved `check_nvidia_api` function from `main.rs` to `product_checker.rs`
  - Split functionality into logical modules for better maintainability
  
### Enhanced Configuration
- Created proper configuration structs in `product_checker.rs`:
  - `ApiConfig`: Main configuration struct for overall settings
  - `HeadersConfig`: HTTP headers configuration for API requests
  - `DefaultLinksConfig`: Default purchase links configuration
  - `RequestConfig`: Request timeout and retry configuration
- Updated configuration loading in `main.rs` to match the structure in `config/default.toml`

### Purchase Integration
- Added new `launch_purchase.rs` module with:
  - `PurchaseConfig` struct to control purchase behavior
  - `launch_purchase` function that initiates the purchase process
  - `should_attempt_purchase` function to determine if a product triggers a purchase

### Testing Capabilities
- Added test mode with the `--test` command-line argument
- Created `simulate_available_product` function for testing purchase workflows
- Added verification of purchase configuration without waiting for actual availability

## Components

The product scanner consists of three main modules:

1. **main.rs**: Application setup, configuration loading, and main loop
   - Handles command-line arguments including test mode
   - Loads configuration from default.toml
   - Sets up logging and error handling
   - Manages the main monitoring loop

2. **product_checker.rs**: API interaction and product availability checking
   - Makes HTTP requests to the NVIDIA API
   - Parses API responses to check product availability
   - Returns product links when products are available
   - Includes test functionality to simulate available products

3. **launch_purchase.rs**: Purchase initiation when products are available
   - Controls purchase behavior through the PurchaseConfig struct
   - Determines which products should trigger purchase attempts
   - Launches the purchase process by calling the Python purchase script
   - Provides logging and error handling for purchase attempts

## Configuration

The product scanner is configured via the `config/default.toml` file:

```toml
# API configuration
[api]
url = "https://api.nvidia.partners/edge/product/availability/v1/DE/de-de/geforce/"
interval_seconds = 5
timeout_seconds = 10
max_retries = 3

# HTTP request headers
[api.headers]
authority = "api.nvidia.partners"
accept = "application/json"
accept_language = "en-US,en;q=0.9"
referer = "https://store.nvidia.com/"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

# Default purchase links
[api.default_links]
rtx_5080 = "https://store.nvidia.com/de-de/geforce/store/?page=1&limit=100&locale=de-de&category=GPU"
rtx_5090 = "https://store.nvidia.com/de-de/geforce/store/?page=1&limit=100&locale=de-de&category=GPU"

# Purchase configuration
[purchase]
enabled = true
product_names = ["NVIDIA RTX 5080", "NVIDIA RTX 5090"]
```

## Usage

### Running in Normal Mode

```bash
# From the product-scanner directory
cargo run --release
```

### Running in Test Mode

```bash
# From the product-scanner directory
cargo run --release -- --test
```

When running in test mode, the scanner will:
1. Simulate availability for configured products
2. Test the purchase initiation process
3. Verify that the product list in configuration is correctly processed
4. Exit after completing the tests

## Integration with the NVIDIA Purchase System

The product scanner works in conjunction with:

1. **Cookie Preparation Tool**: Uses cookies obtained from the cookie-prep component to authenticate API requests
2. **Purchase Core**: Initiates the purchase process when a product becomes available
3. **Coordinator**: Is launched and monitored by the coordinator script for continuous operation

## Dependencies

- Rust (stable channel)
- reqwest: For making HTTP requests
- serde: For JSON serialization/deserialization
- tokio: For async runtime
- config: For configuration management
- chrono: For timestamp handling
- log/env_logger: For logging
