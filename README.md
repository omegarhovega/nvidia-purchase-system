# NVIDIA GPU Purchase System

An automated system for monitoring and purchasing NVIDIA GPUs when they become available.

## Project Structure

This project is organized into four main components:

1. **purchase-core** (Python): Core purchasing functionality
   - HTTP client handling
   - Cookie management
   - Purchase automation

2. **product-scanner** (Rust): Product availability monitoring
   - API monitoring
   - Product tracking
   - Availability notifications
   - Automatic purchase initiation

3. **cookie-prep** (Python): Cookie and session management
   - Use script to inject to nvidia shop homepage and show button using old purchase link
   - Follow old purchase link Using 2Captcha to solve Cloudflare challenge
   - Obtain and save cf_clearance cookie

4. **nvidia_purchase_coordinator.py** (Python): Top-level coordination
   - Orchestrates all system components
   - Manages cookie refreshes on a schedule
   - Starts and monitors product scanner
   - Provides unified logging and error handling

## Setup Instructions

### Prerequisites

- Rust (stable channel)
- Python 3.8+
- Required dependencies (see component-specific READMEs)

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

## Configuration

The system is configured using TOML files:

### Product Scanner Configuration

Located at `product-scanner/config/default.toml`:

```toml
# API URL for NVIDIA product search
url = "https://api.nvidia.partners/edge/product/search?page=1&limit=9&manufacturer_filter=NVIDIA%7E1&category=GPU&locale=de-de&manufacturer=NVIDIA"

# Request settings
[request]
timeout_secs = 30
connect_timeout_secs = 15
max_attempts = 4
sleep_ms_min = 500
sleep_ms_max = 1000

# Default purchase links (when these change, the product is available)
[default_links]
rtx_5070 = "https://marketplace.nvidia.com/de-de/consumer/graphics-cards/nvidia-geforce-rtx-5070/"
rtx_5080 = "https://marketplace.nvidia.com/de-de/consumer/graphics-cards/nvidia-geforce-rtx-5080/"
rtx_5090 = "https://marketplace.nvidia.com/de-de/consumer/graphics-cards/nvidia-geforce-rtx-5090/"

# Purchase settings
[purchase]
enabled = true
product_names = [
    "GeForce RTX 5070",
    "GeForce RTX 5080",
    "GeForce RTX 5090"
]
```

## Usage

### Running the Complete System (Recommended)

The easiest way to run the system is using the coordinator script, which manages all components:

```bash
# From the root directory of the project
python nvidia_purchase_coordinator.py
```

This will:
1. Run the session manager to get fresh cookies
2. Start the product scanner to monitor for available products
3. Periodically refresh cookies (every 12-15 minutes)
4. Handle errors and restart components as needed

### Running Components Individually

#### Running the Product Scanner Directly

```bash
# Run the product scanner in normal mode
cd product-scanner
cargo run

# Run the product scanner in test mode (simulates product availability)
cargo run --bin product-scanner --  --test
cargo run -- --test-error
```

The product scanner will:
1. Monitor the NVIDIA API for product availability
2. When a product becomes available, it will automatically initiate the purchase process
3. Log all activities to both the console and a log file (`nvidia_product_checker.log`)

#### Running Cookie Preparation Manually

```bash
# From the cookie-prep directory
cd cookie-prep
python -c "import asyncio; from cookie_prep.session_manager import main; asyncio.run(main())"
```

#### Testing the Purchase Method

```bash
# From the purchase-core/src directory
cd purchase-core/src
python purchase_method.py [purchase_url]
```

### Test Mode

The test mode simulates product availability without making actual API calls. This is useful for testing the purchase functionality without waiting for products to become available.

When running in test mode, the scanner will:
1. Simulate availability for configured products
2. Test the purchase initiation process
3. Exit after completing the tests

### Testing Purchase Integration

To test the complete purchase flow without waiting for actual product availability:

```bash
# From the product-scanner directory
cd product-scanner
cargo run -- --test
```

This will:
1. Load your configuration from default.toml
2. Simulate an available product (e.g., "GeForce RTX 5080")
3. Trigger the purchase flow by calling purchase_method.py with the product URL
4. Log the results of the test

This test verifies that:
- The product scanner correctly identifies configured products
- The launch_purchase module properly executes the purchase script
- The purchase_method.py script is called with the correct parameters
- The entire purchase flow works end-to-end

You can modify which products are tested by changing the `product_names` list in the `[purchase]` section of your configuration file.

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
2. **product_checker.rs**: API interaction and product availability checking
3. **launch_purchase.rs**: Purchase initiation when products are available

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

3. Handles shutdown:
   - Gracefully stops all components
   - Ensures clean process termination

## Development

Each component can be developed and tested independently. See the component-specific
documentation for development workflows.

## License

[Specify license information]
