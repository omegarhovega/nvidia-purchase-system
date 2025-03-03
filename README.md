# NVIDIA GPU Purchase System

An automated system for monitoring and purchasing NVIDIA GPUs when they become available.

## Project Structure

This project is organized into three main components:

1. **purchase-core** (Rust): Core purchasing functionality
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
3. Set up the Python component:
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
rtx_5080 = "https://marketplace.nvidia.com/de-de/consumer/graphics-cards/nvidia-geforce-rtx-5080/"
rtx_5090 = "https://marketplace.nvidia.com/de-de/consumer/graphics-cards/nvidia-geforce-rtx-5090/"

# Purchase settings
[purchase]
enabled = true
product_names = [
    "GeForce RTX 5080",
    "GeForce RTX 5090"
]
```

## Usage

### Running the Product Scanner

```bash
# Run the product scanner in normal mode
cd product-scanner
cargo run

# Run the product scanner in test mode (simulates product availability)
cargo run -- --test
```

The product scanner will:
1. Monitor the NVIDIA API for product availability
2. When a product becomes available, it will automatically initiate the purchase process
3. Log all activities to both the console and a log file (`nvidia_product_checker.log`)

### Test Mode

The test mode simulates product availability without making actual API calls. This is useful for testing the purchase functionality without waiting for products to become available.

When running in test mode, the scanner will:
1. Simulate availability for configured products
2. Test the purchase initiation process
3. Exit after completing the tests

### Stopping the Scanner

Press `Ctrl+C` to gracefully stop the product scanner.

## Implementation Details

### Product Scanner

The product scanner consists of three main modules:

1. **main.rs**: Application setup, configuration loading, and main loop
2. **product_checker.rs**: API interaction and product availability checking
3. **launch_purchase.rs**: Purchase initiation when products are available

When a product is detected as available, the scanner will:
1. Check if the product is in the configured list of products to purchase
2. If it is, launch the purchase process with the product name and link

### Purchase Core

The purchase core component is responsible for the actual purchase process. It is currently in development and will be integrated with the product scanner in the future.

## Development

Each component can be developed and tested independently. See the component-specific
documentation for development workflows.

## License

[Specify license information]
