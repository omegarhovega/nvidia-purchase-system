# NVIDIA GPU Purchase System

An automated system for monitoring and purchasing NVIDIA GPUs when they become available.

## Project Structure

This project is organized into four main components:

1. **product-scanner** (Rust): Product availability monitoring and automated purchase logic
   - NVIDIA API monitoring
   - Product tracking
   - Availability notifications
   - Automatic purchase function
   - Test mode for validating purchase functionality

2. **cookie-prep** (Python): Cookie and session management
   - Browser automation to solve Cloudflare challenges
   - Automatic cookie acquisition and renewal
   - Captures and manages cf_clearance cookie for direct purchase access

3. **nvidia_purchase_coordinator.py** (Python): Top-level coordination
   - Orchestrates all system components
   - Manages cookie refreshes on a schedule
   - Starts and monitors product scanner
   - Enhanced logging with real-time cookie-prep output capture
   - Sound alerts for important events (availability, errors)

4. **early-warning** (Rust): Monitors for changes in product status before official release
   - Monitors baseline NVIDIA API values
   - Alerts when changes are detected in product status

## Configuration

The system uses TOML files for Rust components and Python configuration files:

### Product Scanner Configuration

Located at `product-scanner/config/default.toml`

The scanner configuration controls:
- API endpoints and timeouts
- Request headers and user agent
- Retry parameters
- Sleep intervals between checks

### Early Warning Configuration

Located at `early-warning/config/default.toml`

The monitoring configuration controls:
- API endpoints for inventory and retailer checks
- SKUs to monitor for availability
- Reference response for comparison

### Cookie Preparation Configuration

Located in `cookie-prep/src/config.py`

The cookie configuration controls:
- Browser type and executable path
- Cookie refresh interval
- 2Captcha API key for automated purchasing

### Coordinator Configuration

Configuration is handled directly in `nvidia_purchase_coordinator.py`

The coordinator configuration controls:
- Component lifecycle and communication
- Unified logging and monitoring
- Configurable sound alert patterns
- Cookie refresh intervals

## Features

### Monitoring System

- Real-time monitoring of NVIDIA's inventory API
- Product availability tracking
- SKU change detection
- Multiple API endpoint support

### Sound Alert System

- Configurable sound alerts for important events:
  - Product availability
  - Early warnings
  - API errors
  - Cookie errors
  - General notifications
- Optional silent mode for unattended operation

## Setup Instructions

### Prerequisites

- Rust (stable channel)
- Python 3.8+
- Brave, Chrome or other Chromium based browser
- 2Captcha API key

### Installation

1. Clone this repository
2. Set up the Rust components:
   ```
   cd purchase-core
   cargo build
   cd ../product-scanner
   cargo build
   ```
3. Set up the Python components:
   ```
   cd cookie-prep
   pip install -r requirements.txt
   ```

## Usage

### Running the Complete System (Recommended)

The easiest way to run the system is using the coordinator script, which manages all components:

```bash
# From the root directory of the project
python nvidia_purchase_coordinator.py

# Run in silent mode (no sound alerts)
python nvidia_purchase_coordinator.py --silent
```

This will:
1. Run the session manager to get fresh cookies
2. Start the product scanner to monitor for available products
3. Periodically refresh cookies (every 12-15 minutes)
4. Launch the purchase process when a product becomes available
5. Handle errors and restart components as needed

### Running Components Individually

#### Running the Product Scanner Directly

```bash
# Run the product scanner in normal mode
cd product-scanner
cargo run
```

The product scanner will:
1. Monitor the NVIDIA API for product availability
2. When a product becomes available, it will automatically initiate the purchase process

#### Running Cookie Preparation Manually

```bash
# From the cookie-prep directory
cd cookie-prep/src
python main.py
```

### Test Mode

The product scanner includes a robust test mode that can be activated with the `--test` command-line argument:

```bash
# Run the product scanner in test mode
cd product-scanner
cargo run --bin product-scanner --  --test
```

When running in test mode, the scanner will:
1. Simulate availability for configured products
2. Test the purchase initiation process by calling the purchase mechanism
3. Verify that the product list in configuration is correctly processed
4. Test that purchases are only attempted for configured products
5. Exit after completing the tests

This test mode is useful for:
- Verifying that your purchase configuration is correct
- Testing the complete purchase flow without waiting for actual product availability
- Confirming that the integration between components works as expected

### Stopping the System

Press `Ctrl+C` to gracefully stop all components.

## Implementation Details

### System Architecture

The system operates as a pipeline:

1. **Cookie Preparation**: Obtains and maintains valid Cloudflare cookies
2. **Product Scanner**: Continuously monitors for product availability
3. **Purchase Process**: When a product is available, automatically attempts to purchase it

### Component Integration

- When the product scanner detects an available product, it calls the purchase_method.py script with the purchase link
- The coordinator script ensures cookies are constantly refreshed to maintain session validity
- All components share cookies through the shared/scripts/captured_cookies.json file

### Product Scanner

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

### Purchase Core

The purchase core component handles the actual purchase process:

1. **purchase_method.py**: 
   - Loads cookies from shared/scripts/captured_cookies.json
   - Makes authenticated requests to purchase links
   - Follows redirects and maintains session state
   - Logs results and saves updated cookies

### Cookie Preparation

The cookie-prep component handles browser automation to solve Cloudflare challenges:

1. **session_manager.py**:
   - Uses browser automation to navigate to NVIDIA website
   - Handles Cloudflare challenges and CAPTCHAs
   - Saves cookies to shared/scripts/captured_cookies.json

### Coordinator

The coordinator (nvidia_purchase_coordinator.py) orchestrates the entire system:

1. Handles startup sequence:
   - First runs session_manager to get initial cookies
   - Then starts the product scanner

2. Manages runtime operations:
   - Runs cookie refresh on a schedule (12-15 minute intervals)
   - Monitors product scanner health
   - Provides consolidated logging
   - Captures and displays cookie-prep output in real-time

3. Handles shutdown:
   - Gracefully stops all components

## Project Status

As of April 8, 2025, the project has successfully implemented:

1. Comprehensive product scanning functionality
2. Automatic purchase initiation when products are available
3. Integration between the product scanner and purchase components
4. Cookie management and Cloudflare bypass
5. Full test suite for verifying functionality

The system is capable of:
- Monitoring NVIDIA API for product availability
- Automatically initiating purchases when configured products are available
- Successfully maintaining authenticated sessions with Cloudflare protection
- Performing end-to-end testing of the purchase flow

## Development

Each component can be developed and tested independently. See the component-specific
documentation for development workflows.